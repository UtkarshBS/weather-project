from flask import Flask, request, jsonify
from src.services.db_utils import fetch_query
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Returns weather data from the database, filtered by station_id and date (if provided), and paginated.
    Have added station level filter and date level filter because I don't think anyone would be querying for the whole database like ever?
    Doesn't make sense on a product use case at least. So I have added that limitation.
    """
    station_id = request.args.get('station_id')
    date = request.args.get('date')
    limit = int(request.args.get('limit', 10)) 
    offset = int(request.args.get('offset', 0))


    if not station_id and not date:
        return jsonify({'error': 'Please provide at least one filter: station_id or date.'}), 400

    # Build the query with optional filters for station_id and date
    query = "SELECT station_id, date, max_temp, min_temp, precipitation FROM weather_data WHERE 1=1"
    params = []

    if station_id:
        query += " AND station_id = %s"
        params.append(station_id)
    if date:
        query += " AND date = %s"
        params.append(date)

    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    weather_data = fetch_query(query, tuple(params))

    # Converting the data to JSON format in a slightly primitive manner, I'm sorry. Again, it's 6AM.
    weather_json = []
    for row in weather_data:
        weather_json.append({
            'station_id': row[0],
            'date': row[1].isoformat(),
            'max_temp': row[2],
            'min_temp': row[3],
            'precipitation': row[4]
        })

    return jsonify(weather_json)


@app.route('/api/weather/stats', methods=['GET'])
def get_weather_stats():
    """
    Returns weather statistics from the database, filtered by station_id and year (if provided), and paginated.
    
    Again, same things that I wrote above still apply here.
    """
    station_id = request.args.get('station_id')
    year = request.args.get('year')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    if not station_id and not year:
        return jsonify({'error': 'Please provide at least one filter: station_id or year.'}), 400

    query = "SELECT station_id, year, avg_max_temp, avg_min_temp, total_precipitation FROM weather_yearly_stats WHERE 1=1"
    params = []

    if station_id:
        query += " AND station_id = %s"
        params.append(station_id)
    if year:
        query += " AND year = %s"
        params.append(year)

    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    stats_data = fetch_query(query, tuple(params))

    stats_json = []
    for row in stats_data:
        stats_json.append({
            'station_id': row[0],
            'year': row[1],
            'avg_max_temp': row[2],
            'avg_min_temp': row[3],
            'total_precipitation': row[4]
        })

    return jsonify(stats_json)

if __name__ == '__main__':
    app.run(debug=True)
