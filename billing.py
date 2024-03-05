import cv2
import os
import sys
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import RPi.GPIO as GPIO
from hx711 import HX711
import requests
import json
from requests.structures import CaseInsensitiveDict
import getopt


runner = None
show_camera = True

c_value = 0
flag = 0
ratio=-1363.992

global id_product
id_product = 1
list_label = []
list_weight = []
count = 0
final_weight = 0
taken = 1

a = 'tomato'
b = 'Banana'
l = 'Lays'
c = 'Coke'

def now():
    return round(time.time() * 1000)

def get_webcams():
    port_ids = []
    port = 0
    print("Looking for a camera in port %s:" % port)
    camera = cv2.VideoCapture(port)
    if camera.isOpened():
        ret = camera.read()[0]
        if ret:
            backendName = camera.getBackendName()
            w = camera.get(3)
            h = camera.get(4)
            print("Camera %s (%s x %s) found in port %s " % (backendName, h, w, port))
            port_ids.append(port)
        camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def find_weight():
    global c_value
    global hx
    if c_value == 0:
        print('Calibration starts')
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)  # Suppress warnings
            hx = HX711(5, 6)
            err = hx.zero()
            if err:
                raise ValueError('Tare is unsuccessful.')
            hx.set_scale_ratio(ratio)
            c_value = 1
        except (KeyboardInterrupt, SystemExit):
            print('Bye :)')
        print('Calibrate ends')
    else:
        GPIO.setmode(GPIO.BCM)
        time.sleep(1)
        try:
            weight = int(hx.get_weight_mean(20))
            abs_weight = abs(weight)
            print(abs_weight, 'g')
            return abs_weight
        except (KeyboardInterrupt, SystemExit):
            print('Bye :)')

def post(label, price, final_rate, taken):
    global id_product
    url = "http://127.0.0.1:5000/products"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data_dict = {
        "id": id_product,
        "name": label,
       "price": price,
        "units": str(taken),
        "taken": taken,
        "payable": str(final_rate)
    }
    data = json.dumps(data_dict)
    resp = requests.post(url, headers=headers, data=data)
    print(resp.status_code)
    id_product = id_product + 1
    time.sleep(1)
    list_label = []
    list_weight = []
    count = 0
    final_weight = 0
    taken = 0

def list_com(label, final_weight):
    global count
    global taken
    global list_weight

    list_weight.append(final_weight)

    if len(list_weight) > 1 and abs(list_weight[-1]) > 2 and abs(list_weight[-1]) > abs(list_weight[-2]):
        taken += 1

    if count > 0 and list_label[-1] != list_label[-2]:
        print("New Item detected")
        print("Final weight is", list_weight[-2])
        rate(list_weight[-2], list_label[-2], taken)
        list_weight = []
        taken = 0

    list_label.append(label)
    count += 1
    print('count is', count)


def rate(final_weight, label, taken):
    print("Calculating rate")
    if label == a:
        print("Calculating rate of", label)
        final_rate_a = final_weight * 0.01
        price = 10
        print(final_rate_a)
        post(label, price, final_rate_a, taken)
    elif label == b:
        print("Calculating rate of", label)
        final_rate_b = final_weight * 0.02
        price = 20
        post(label, price, final_rate_b, taken)
    elif label == l:
        print("Calculating rate of", label)
        final_rate_l = 1
        price = 10
        post(label, price, final_rate_l, taken)
    else:
        print("Calculating rate of", label)
        final_rate_c = 2
        price = 20
        post(label, price, final_rate_c, taken)

def main(argv):
    global flag
    global final_weight
    if flag == 0:
        find_weight()
        flag = 1
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            break  # Exit the loop but continue with the script
   
    if len(args) == 0:
        print("Usage: python classify.py <path_to_model.eim> [<Camera port ID, only required when more than 1 camera is present>]")

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)
   
    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args) >= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args) <= 1 and len(port_ids) > 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." % (backendName, h, w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0
            #print(next_frame)

            for res, img in runner.classifier(videoCaptureDeviceId):
               
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)

                #print('classification runner response', res)

                if "bounding_boxes" in res["result"].keys():
                    for bbox in res["result"]["bounding_boxes"]:
                        label = bbox["label"]
                        score = bbox["value"]
                        if score > 0.7:
                            final_weight = find_weight()
                            list_com(label, final_weight)  # Pass final_weight here
                           
                            if label == a:
                               print('Tomato detected')
                            elif label == b:
                                print('Banana detected')
                            elif label == l:
                                print('Lays detected')
                            else:
                                print('Coke detected')
                            print(final_weight)
                            print(taken)    
   
                            rate(final_weight, label, taken)
                            return
                    print('', flush=True)
                next_frame = now() + 100
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
