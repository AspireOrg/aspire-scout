from scout.site.factory import create_app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get('PORT', 8182)
    app.run(host="0.0.0.0", port=port)
