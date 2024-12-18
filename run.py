'''
run.py

This file runs the application.
'''

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        ssl_context=('cert.pem', 'key.pem'),
        debug=True, 
        host='0.0.0.0', 
        port=443
    )
