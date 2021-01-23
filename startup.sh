#!/bin/sh
echo "setting up some dev environment variables..."

export FLASK_APP=server
export FLASK_DEBUG=1
export FLASK_ENV=development

. venv/bin/activate

echo "setup complete!"