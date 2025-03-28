#!/usr/bin/env python
"""Run the Puzzle Fact Check API server"""

from api.app import app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True) 