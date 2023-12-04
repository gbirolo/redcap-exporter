from flask import Flask, Blueprint, request, render_template, send_file
from werkzeug.utils import secure_filename
from .convert import convert

from io import BytesIO
import os
import random

def get_random_dir(prefix):
    while True:
        i = random.randint(10000, 99999)
        path = prefix + f'{i}/'
        print('pp', path)
        try:
            os.makedirs(path, exist_ok=False)
            return path
        except FileExistsError:
            pass


from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)#, instance_relative_config=True)

    # proxy
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    #app.config.from_pyfile('config.py', silet=True)
    #bp = Blueprint('conv', __name__)

    #app.register_blueprint(bp)

    @app.route('/')
    def submission():

        return render_template('upload.html')

    @app.route('/converted', methods=('POST',))
    def conversion():
        #dirpath = get_random_dir('results/')

        if 'file' in request.files:
            file = request.files['file']

            output_name = secure_filename(file.filename)
            if output_name.endswith('.csv'):
                output_name = output_name[:-3] + 'xlsx'
            
            output = BytesIO()
            convert(file.stream, output)

            # download file
            output.seek(0)
            return send_file(output, download_name=output_name)
            
        #return render_template('download.html', output_name='ciccia')

    return app

#if __name__ == '__main__':
#    app = create_app()
#    app.run(debug=False, port=10060)