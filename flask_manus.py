from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from trust_manus import SemanticAcademicSearchEngine
import numpy as np
import time

# Initialize the search engine globally
search_engine = None

def initialize_search_engine():
    """Initialize the search engine and make it globally accessible"""
    global search_engine
    search_engine = SemanticAcademicSearchEngine()
    return search_engine

# Initialize the engine when the app starts
search_engine = initialize_search_engine()

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def convert_similarity_threshold(threshold_str):
    """Convert string threshold to numeric value"""
    threshold_map = {
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4
    }
    return threshold_map.get(threshold_str, 0.6)

def sanitize_for_json(obj):
    """
    🧹 JSON SERIALIZATION SANITIZER
    
    Convert NumPy types and other non-JSON-serializable objects to Python natives.
    Because Flask jsonify() is picky about data types like a academic peer reviewer.
    """
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, str):
        return str(obj)
    elif obj is None:
        return None
    else:
        # For any other type, convert to string as a fallback
        return str(obj)

# Home route
@app.route('/')
def home():
    return send_from_directory('.', 'manus_index_search_engine.html')

# Serve UI functions
@app.route('/manus_ui-functions.js')
def serve_ui_functions():
    return send_from_directory('.', 'manus_ui-functions.js')

# Debug route
@app.route('/debug')
def debug_info():
    return jsonify({
        'message': 'Flask app is alive and functional!',
        'available_routes': [str(rule) for rule in app.url_map.iter_rules()],
        'static_files_served_from': '.'
    })

# Main unified search endpoint (GET method for frontend compatibility)
@app.route('/api/search', methods=['GET'])
def api_search():
    try:
        keyword = request.args.get('keyword', '')
        max_results = int(request.args.get('max_results', 20))
        similarity_threshold_str = request.args.get('similarity_threshold', 'medium')
        sources_param = request.args.get('sources', 'dergipark,trdizin,yoktez')
        
        # Convert similarity threshold
        similarity_threshold = convert_similarity_threshold(similarity_threshold_str)
        
        # Parse sources
        sources = sources_param.split(',')
        
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        if len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'}), 400

        print(f"🔍 API Search Request: keyword='{keyword}', sources={sources}, max_results={max_results}, threshold={similarity_threshold}")

        # Perform unified search
        results = search_engine.unified_semantic_search(
            keyword=keyword,
            sources=sources,
            dergipark_results=max_results,
            trdizin_results=max_results,
            yoktez_results=max_results,
            similarity_threshold=similarity_threshold
        )
        
        # 🧹 Sanitize results for JSON serialization
        clean_results = sanitize_for_json(results)
        
        return jsonify(clean_results)
        
    except Exception as e:
        print(f"💥 API Search Error: {e}")
        return jsonify({'error': str(e)}), 500

# Dergipark-only search endpoint
@app.route('/api/dergipark', methods=['GET'])
def api_dergipark():
    try:
        keyword = request.args.get('keyword', '')
        max_results = int(request.args.get('max_results', 20))
        similarity_threshold_str = request.args.get('similarity_threshold', 'medium')
        
        similarity_threshold = convert_similarity_threshold(similarity_threshold_str)
        
        if not keyword or len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'}), 400

        print(f"📚 Dergipark Search: keyword='{keyword}', max_results={max_results}")

        # Search only Dergipark
        dergipark_results = search_engine.semantic_search_dergipark(
            keyword=keyword,
            max_results=max_results,
            similarity_threshold=similarity_threshold
        )
        
        # Format response to match unified structure
        response = {
            "keyword": keyword,
            "search_type": "dergipark_only",
            "similarity_threshold": similarity_threshold,
            "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "dergipark": {
                    "total_results": len(dergipark_results),
                    "search_type": "semantic_vector_similarity",
                    "results": dergipark_results
                }
            },
            "summary": {
                "total_articles_found": len(dergipark_results),
                "dergipark_semantic_count": len(dergipark_results)
            }
        }
        
        # 🧹 Sanitize for JSON serialization
        clean_response = sanitize_for_json(response)
        return jsonify(clean_response)
        
    except Exception as e:
        print(f"💥 Dergipark API Error: {e}")
        return jsonify({'error': str(e)}), 500

# TRDizin-only search endpoint
@app.route('/api/trdizin', methods=['GET'])
def api_trdizin():
    try:
        keyword = request.args.get('keyword', '')
        max_results = int(request.args.get('max_results', 20))
        similarity_threshold_str = request.args.get('similarity_threshold', 'medium')
        
        similarity_threshold = convert_similarity_threshold(similarity_threshold_str)
        
        if not keyword or len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'}), 400

        print(f"🇹🇷 TRDizin Search: keyword='{keyword}', max_results={max_results}")

        # Search only TRDizin
        trdizin_results = search_engine.semantic_search_trdizin(
            keyword=keyword,
            top_k=max_results,
            similarity_threshold=similarity_threshold
        )
        
        # Format response to match unified structure
        response = {
            "keyword": keyword,
            "search_type": "trdizin_only",
            "similarity_threshold": similarity_threshold,
            "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "trdizin": {
                    "total_results": len(trdizin_results),
                    "search_type": "bilingual_semantic_vector_similarity",
                    "results": trdizin_results
                }
            },
            "summary": {
                "total_articles_found": len(trdizin_results),
                "trdizin_semantic_count": len(trdizin_results)
            }
        }
        
        # 🧹 Sanitize for JSON serialization
        clean_response = sanitize_for_json(response)
        return jsonify(clean_response)
        
    except Exception as e:
        print(f"💥 TRDizin API Error: {e}")
        return jsonify({'error': str(e)}), 500

# YÖK Tez-only search endpoint
@app.route('/api/yoktez', methods=['GET'])
def api_yoktez():
    try:
        keyword = request.args.get('keyword', '')
        max_results = int(request.args.get('max_results', 20))
        
        if not keyword or len(keyword) < 3:
            return jsonify({'error': 'Keyword must be at least 3 characters'}), 400

        print(f"🎓 YÖK Tez Search: keyword='{keyword}', max_results={max_results}")

        # Search YÖK Tez live
        yoktez_results = search_engine.search_yok_tez_live(
            keyword=keyword,
            max_results=max_results
        )
        
        # Format response to match unified structure
        response = {
            "keyword": keyword,
            "search_type": "yoktez_only",
            "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "yoktez": {
                    "total_results": len(yoktez_results),
                    "search_type": "yoktez_online",
                    "results": yoktez_results
                }
            },
            "summary": {
                "total_articles_found": len(yoktez_results),
                "yoktez_count": len(yoktez_results)
            }
        }
        
        # 🧹 Sanitize for JSON serialization
        clean_response = sanitize_for_json(response)
        return jsonify(clean_response)
        
    except Exception as e:
        print(f"💥 YÖK Tez API Error: {e}")
        return jsonify({'error': str(e)}), 500

# Original POST endpoint (keeping for backward compatibility)
@app.route('/search', methods=['POST'])
def unified_search_api():
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        sources = data.get('sources', [])
        dergipark_results = data.get('dergipark_results', 15)
        trdizin_results = data.get('trdizin_results', 15)
        yoktez_results = data.get('yoktez_results', 15)
        similarity_threshold = data.get('similarity_threshold', 0.7)

        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        if not sources:
            return jsonify({'error': 'At least one source must be selected'}), 400

        results = search_engine.unified_semantic_search(
            keyword=keyword,
            sources=sources,
            dergipark_results=dergipark_results,
            trdizin_results=trdizin_results,
            yoktez_results=yoktez_results,
            similarity_threshold=similarity_threshold
        )
        
        # 🧹 Sanitize for JSON serialization
        clean_results = sanitize_for_json(results)
        return jsonify(clean_results)
        
    except Exception as e:
        print(f"💥 Unified Search API Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("🔥 FIRING UP THE UNIFIED FLASK EMPIRE!")
    print("   Your search interface: http://localhost:4000")
    print("   API endpoints:")
    print("     - GET  /api/search")
    print("     - GET  /api/dergipark")  
    print("     - GET  /api/trdizin")
    print("     - GET  /api/yoktez")
    print("     - POST /search")
    print("   Debug info: http://localhost:4000/debug")
    app.run(host='0.0.0.0', port=4000, debug=True)