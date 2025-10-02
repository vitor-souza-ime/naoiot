import qi
import torch
from PIL import Image
import numpy as np
import time
import os
import requests
from datetime import datetime
from transformers import BlipProcessor, BlipForConditionalGeneration

# IMPORTANTE: Configurar matplotlib ANTES de importar pyplot
import matplotlib
matplotlib.use('Agg')  # Backend sem GUI
import matplotlib.pyplot as plt

# Resto do código permanece igual...
THINGSPEAK_API_KEY = "YOUR_API_KEY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

FIRE_KEYWORDS = [
    'fire', 'flame', 'flames', 'burning', 'smoke', 'smoky',
    'blaze', 'inferno', 'combustion', 'ignition', 'smoldering'
]

def setup_output_directory():
    """Cria diretório para salvar as imagens"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"nao_fire_detection_{timestamp}"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Diretório criado: {output_dir}")
    
    return output_dir

def detect_fire_in_caption(caption):
    """Verifica se a legenda contém palavras relacionadas a fogo"""
    caption_lower = caption.lower()
    for keyword in FIRE_KEYWORDS:
        if keyword in caption_lower:
            return True, keyword
    return False, None

def send_fire_alert_to_thingspeak(caption, blip_time, detected_keyword):
    """Envia alerta de fogo para ThingSpeak e mede latência HTTP"""
    try:
        http_start_time = time.time()
        #url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1=1&field2={blip_time:.2f}&field3={int(time.time())}"
        url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1=1"
        response = requests.get(url, timeout=10)
        http_latency = (time.time() - http_start_time) * 1000
        
        if response.status_code == 200:
            print(f"\n{'='*60}")
            print(f"🚨 ALERTA DE FOGO ENVIADO COM SUCESSO!")
            print(f"{'='*60}")
            print(f"Palavra-chave detectada: '{detected_keyword}'")
            print(f"Legenda completa: '{caption}'")
            print(f"⏱️  Tempo de detecção BLIP: {blip_time:.2f} ms")
            print(f"⏱️  Latência HTTP: {http_latency:.2f} ms")
            print(f"⏱️  Tempo total: {(blip_time + http_latency):.2f} ms")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Response: {response.text}")
            print(f"{'='*60}\n")
            return True, http_latency
        else:
            print(f"✗ Erro ao enviar alerta: Status {response.status_code}")
            return False, http_latency
            
    except Exception as e:
        http_latency = (time.time() - http_start_time) * 1000 if 'http_start_time' in locals() else 0
        print(f"✗ Erro ao enviar para ThingSpeak: {e}")
        return False, http_latency

def save_fire_detection(image, output_dir, iteration, caption, blip_time, http_latency):
    """Salva imagem com informações de detecção de fogo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FIRE_ALERT_{iteration:04d}_{timestamp}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    image.save(filepath, quality=95)
    
    log_filename = f"FIRE_ALERT_{iteration:04d}_{timestamp}.txt"
    log_filepath = os.path.join(output_dir, log_filename)
    with open(log_filepath, 'w', encoding='utf-8') as f:
        f.write(f"🚨 ALERTA DE FOGO DETECTADO\n")
        f.write(f"{'='*50}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Iteração: {iteration}\n")
        f.write(f"Caption: {caption}\n")
        f.write(f"Tempo de detecção BLIP: {blip_time:.2f} ms\n")
        f.write(f"Latência HTTP ThingSpeak: {http_latency:.2f} ms\n")
        f.write(f"Tempo total: {(blip_time + http_latency):.2f} ms\n")
        f.write(f"{'='*50}\n")
    
    print(f"✓ Alerta salvo: {filepath}")
    return filepath

def save_monitoring_image(image, output_dir, iteration, caption, fire_detected, blip_time, http_latency):
    """Salva imagem de monitoramento com informações visuais"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    bg_color = "red" if fire_detected else "lightgreen"
    status = "🚨 FOGO DETECTADO!" if fire_detected else "✓ Normal"
    
    ax1.imshow(image)
    ax1.axis('off')
    title = f"NAO Fire Detection - {status} - Iter {iteration} - {datetime.now().strftime('%H:%M:%S')}"
    ax1.set_title(title, fontsize=14, fontweight='bold', 
                  color='red' if fire_detected else 'black')
    
    text_content = f"Caption: {caption}\n"
    if fire_detected:
        text_content += f"\n⏱️ BLIP Time: {blip_time:.2f} ms\n"
        text_content += f"⏱️  HTTP Latency: {http_latency:.2f} ms\n"
        text_content += f"⏱️  Total: {(blip_time + http_latency):.2f} ms"
    
    ax2.text(0.5, 0.5, text_content,
             horizontalalignment='center', verticalalignment='center',
             fontsize=11, wrap=True, transform=ax2.transAxes,
             bbox=dict(boxstyle="round,pad=0.5", facecolor=bg_color, alpha=0.8))
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    plt.tight_layout()
    
    # Salvar imagem ao invés de mostrar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_filename = f"monitor_{iteration:04d}_{timestamp}.png"
    img_filepath = os.path.join(output_dir, img_filename)
    plt.savefig(img_filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return img_filepath

def connect_to_nao(ip="172.15.1.29", port=9559):
    """Conecta ao robô NAO"""
    session = qi.Session()
    session.connect(f"tcp://{ip}:{port}")
    return session

def capture_image_from_nao(session):
    """Captura uma imagem da câmera do NAO"""
    try:
        camera_service = session.service("ALVideoDevice")
        
        camera_id = 0
        resolution = 2
        color_space = 11
        fps = 5
        
        try:
            video_client = camera_service.subscribeCamera("python_client", camera_id, resolution, color_space, fps)
        except AttributeError:
            try:
                video_client = camera_service.subscribe("python_client", resolution, color_space, fps)
            except AttributeError:
                video_client = "python_client"
                camera_service.setActiveCamera(camera_id)
                camera_service.setResolution(video_client, resolution)
                camera_service.setColorSpace(video_client, color_space)
                camera_service.setFrameRate(video_client, fps)
        
        time.sleep(0.1)
        nao_image = camera_service.getImageRemote(video_client)
        
        if nao_image is None or len(nao_image) < 7:
            raise Exception("Falha ao capturar imagem da câmera")
        
        width = nao_image[0]
        height = nao_image[1]
        channels = nao_image[2]
        image_data = nao_image[6]
        
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image_array = image_array.reshape((height, width, channels))
        image = Image.fromarray(image_array).convert("RGB")
        
        return image
        
    except Exception as e:
        print(f"Erro na captura da imagem: {e}")
        return Image.new('RGB', (640, 480), color='blue')
    
    finally:
        try:
            if 'video_client' in locals() and hasattr(camera_service, 'unsubscribe'):
                camera_service.unsubscribe(video_client)
        except:
            pass

def speak_text(session, text):
    """Faz o robô falar o texto"""
    try:
        tts_service = session.service("ALTextToSpeech")
        try:
            tts_service.setLanguage("English")
        except:
            pass
        tts_service.setVolume(0.8)
        tts_service.say(text)
    except Exception as e:
        print(f"Erro na síntese de voz: {e}")

def main():
    print("="*60)
    print("🔥 SISTEMA DE DETECÇÃO DE FOGO NAO + THINGSPEAK")
    print("="*60)
    print("ℹ️  Modo sem GUI - Imagens serão salvas no diretório")
    
    output_dir = setup_output_directory()
    
    print("\nConectando ao NAO...")
    try:
        session = connect_to_nao("172.15.1.29", 9559)
        print("✓ Conectado com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        return
    
    print("\nCarregando modelo BLIP...")
    try:
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
        print("✓ Modelo BLIP carregado!")
    except Exception as e:
        print(f"✗ Erro ao carregar modelo: {e}")
        return
    
    print("\n" + "="*60)
    print("🔍 SISTEMA ATIVO - Monitorando ambiente para detecção de fogo")
    print("="*60)
    print("Pressione Ctrl+C para parar\n")
    
    iteration = 1
    fire_detection_count = 0
    
    try:
        while True:
            print(f"--- Iteração {iteration} ---")
            
            image = capture_image_from_nao(session)
            
            blip_start_time = time.time()
            inputs = processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                output = model.generate(**inputs, max_length=50)
                caption = processor.decode(output[0], skip_special_tokens=True)
            
            blip_time = (time.time() - blip_start_time) * 1000
            print(f"✓ Legenda: '{caption}' (Tempo BLIP: {blip_time:.2f} ms)")
            
            fire_detected, detected_keyword = detect_fire_in_caption(caption)
            http_latency = 0
            
            if fire_detected:
                fire_detection_count += 1
                print(f"\n🚨 FIRE DETECTED (Detection #{fire_detection_count})")
                
                alert_sent, http_latency = send_fire_alert_to_thingspeak(caption, blip_time, detected_keyword)
                
                if alert_sent:
                    save_fire_detection(image, output_dir, iteration, caption, blip_time, http_latency)
                
                alert_message = f"Fire detected! {caption}"
                speak_text(session, alert_message)
            
            else:                
                url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1=0"
                response = requests.get(url, timeout=10)

            # Salvar imagem de monitoramento
            save_monitoring_image(image, output_dir, iteration, caption, fire_detected, blip_time, http_latency)
            
            time.sleep(10)
            iteration += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
        print(f"Total de detecções de fogo: {fire_detection_count}")
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
    
    print(f"\nSistema finalizado! Alertas salvos em: {output_dir}")

if __name__ == "__main__":
    main()
