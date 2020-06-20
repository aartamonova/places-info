import os
from places_info import app, index_routes, errors_routes, auth_routes, statistic_routes, tags_routes, places_routes

app.register_blueprint(index_routes.bp)
app.register_blueprint(errors_routes.bp)
app.register_blueprint(auth_routes.bp)
app.register_blueprint(statistic_routes.bp)
app.register_blueprint(tags_routes.bp)
app.register_blueprint(places_routes.bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
