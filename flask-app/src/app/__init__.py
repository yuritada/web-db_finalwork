from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # 設定の読み込み
    app.config.from_object('app.config.Config')

    # ルートの登録
    with app.app_context():
        from . import routes

    return app

app = create_app()