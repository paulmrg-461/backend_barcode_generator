import sys
import json
import io

from flask import Flask, jsonify, request, send_file, current_app as app
from flask_restful import Api, Resource
import pandas as pd
from flask_cors import CORS, cross_origin
import code128
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

api = Api(app)

def generate_barcode(bc):
    return bc

def generate_name(name):
    return name
    
@app.route('/api/upload-excel-file', methods = ['GET','POST'])
@cross_origin()
def upload_excel_file():
    file = request.files['file']
    company_name = request.args.get('company_name')  
    try:
        dataframe = pd.read_excel(
            file,
            engine='openpyxl',
            dtype=str,
            keep_default_na=True
        )
        dataframe.dropna(how='all', inplace=True)

        barcode_list = []
        name_list = []
        image_list = []
        barcode_list = dataframe['barcode'].apply(lambda x: generate_barcode(x))
        name_list = dataframe['name'].apply(lambda x: generate_name(x))

        for i, bc in enumerate(barcode_list):
            barcode_image = code128.image(f"{bc}", height=100)

            # Create empty image for barcode + text
            top_bott_margin = 35
            l_r_margin = 10
            new_height = barcode_image.height + (2 * top_bott_margin)
            new_width = barcode_image.width + (2 * l_r_margin)
            new_image = Image.new( 'RGB', (new_width, new_height), (255, 255, 255))

            # put barcode on new image
            barcode_y = 42
            new_image.paste(barcode_image, (0, barcode_y))

            # object to draw text
            draw = ImageDraw.Draw(new_image)

            # Define custom text size and font
            h1_size = 24
            h2_size = 28
            h3_size = 12
            footer_size = 18

            h1_font = ImageFont.truetype("/home/files/fonts/DejaVuSans-Bold.ttf", h1_size)
            h2_font = ImageFont.truetype("/home/files/fonts/Ubuntu-C.ttf", h2_size)
            h3_font = ImageFont.truetype("/home/files/fonts/Ubuntu-C.ttf", h3_size)
            footer_font = ImageFont.truetype("/home/files/fonts/UbuntuMono-R.ttf", footer_size)

            # Define custom text
            product_type = f'{name_list[i]}'
            center_product_type = (barcode_image.width / 2) - len(product_type) * 5
            center_barcode_value = (barcode_image.width / 2) - len(f"{bc}") * 8

            # Draw text on picture
            draw.text( (l_r_margin, 0), company_name, fill=(0, 0, 0), font=h3_font)
            draw.text( (center_product_type, (20)), product_type, fill=(0, 0, 0), font=footer_font)
            draw.text( (center_barcode_value, (new_height - 30)), f"{bc}", fill=(0, 0, 0), font=h1_font)
            image_list.append(new_image)

        local_path = "/home/files/BarcodeList.pdf"
        image_list[0].save(local_path, save_all=True, append_images=image_list)
        with open(local_path, "rb") as fh:
            buf = io.BytesIO(fh.read())
            return send_file(
                buf,
                mimetype='application/pdf'
            )
        
        # return "done"
    except Exception as ex:
        print('Exception:')
        print(ex, file=sys.stderr)
        retMap = {
            'success': False,
            'error': f"(Error: {ex})",
            'status code': 200
        }
        return jsonify(retMap)

@app.route('/api/download-template', methods = ['GET'])
@cross_origin()
def download_template():
    local_path = "/home/files/Template.xlsx"
        
    try:
        with open(local_path, "rb") as fh:
            buf = io.BytesIO(fh.read())
            return send_file(
                buf,
                mimetype='application/xlsx',
                as_attachment=True,
                attachment_filename="Template.xlsx"
            )
        
        # return "done"
    except Exception as ex:
        print('Exception:')
        print(ex, file=sys.stderr)
        retMap = {
            'success': False,
            'error': f"(Error: {ex})",
            'status code': 200
        }
        return jsonify(retMap)


@app.route('/')
def welcome():
    return 'Barcode Generator Rest API!'  

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1616)
