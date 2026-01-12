import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, AttackTechnique, AtomicTest
from services import AtomicRedTeamService, LLMService
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///atomic_rt.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize services
atomic_service = AtomicRedTeamService(
    os.getenv('ATOMIC_RED_TEAM_REPO', 'https://raw.githubusercontent.com/redcanaryco/atomic-red-team/master')
)
llm_service = LLMService(
    api_key=os.getenv('OPENAI_API_KEY', ''),
    api_base=os.getenv('OPENAI_API_BASE'),
    model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
)


# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/techniques', methods=['GET'])
def get_techniques():
    """Get all attack techniques"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = AttackTechnique.query
    
    if search:
        query = query.filter(
            (AttackTechnique.technique_id.contains(search)) |
            (AttackTechnique.name.contains(search)) |
            (AttackTechnique.description.contains(search))
        )
    
    pagination = query.order_by(AttackTechnique.technique_id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'techniques': [t.to_dict() for t in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@app.route('/api/techniques/<technique_id>', methods=['GET'])
def get_technique(technique_id):
    """Get a specific technique"""
    technique = AttackTechnique.query.filter_by(technique_id=technique_id).first()
    
    if not technique:
        return jsonify({'error': 'Technique not found'}), 404
    
    technique_dict = technique.to_dict()
    technique_dict['atomic_tests'] = [test.to_dict() for test in technique.atomic_tests]
    
    return jsonify(technique_dict)


@app.route('/api/techniques/sync', methods=['POST'])
def sync_techniques():
    """Sync techniques from Atomic Red Team repository"""
    try:
        data = request.get_json() or {}
        technique_ids = data.get('technique_ids', [])
        
        # Default limit for syncing (configurable via environment or request)
        default_sync_limit = int(os.getenv('SYNC_LIMIT', '10'))
        
        if not technique_ids:
            technique_ids = atomic_service.fetch_technique_list()[:default_sync_limit]
        
        synced = []
        errors = []
        
        for technique_id in technique_ids:
            try:
                # Fetch technique data
                raw_data = atomic_service.fetch_technique_data(technique_id)
                if not raw_data:
                    errors.append(f"{technique_id}: Failed to fetch data")
                    continue
                
                parsed_data = atomic_service.parse_technique_data(raw_data)
                if not parsed_data:
                    errors.append(f"{technique_id}: Failed to parse data")
                    continue
                
                # Check if technique exists
                technique = AttackTechnique.query.filter_by(
                    technique_id=parsed_data['technique_id']
                ).first()
                
                if not technique:
                    technique = AttackTechnique()
                
                # Update technique
                technique.technique_id = parsed_data['technique_id']
                technique.name = parsed_data['name']
                technique.description = parsed_data['description']
                technique.tactic = parsed_data['tactic']
                technique.platform = parsed_data['platform']
                technique.raw_data = parsed_data['raw_data']
                
                db.session.add(technique)
                db.session.flush()
                
                # Delete old atomic tests
                AtomicTest.query.filter_by(technique_id=technique.technique_id).delete()
                
                # Add atomic tests
                for test_data in parsed_data['atomic_tests']:
                    test = AtomicTest(
                        technique_id=technique.technique_id,
                        test_number=test_data['test_number'],
                        name=test_data['name'],
                        description=test_data['description'],
                        supported_platforms=test_data['supported_platforms'],
                        executor=test_data['executor'],
                        command=test_data['command']
                    )
                    db.session.add(test)
                
                db.session.commit()
                synced.append(technique_id)
                
            except Exception as e:
                db.session.rollback()
                errors.append(f"{technique_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'synced': synced,
            'errors': errors,
            'count': len(synced)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/techniques/<technique_id>/analyze', methods=['POST'])
def analyze_technique(technique_id):
    """Analyze a technique using LLM"""
    try:
        technique = AttackTechnique.query.filter_by(technique_id=technique_id).first()
        
        if not technique:
            return jsonify({'error': 'Technique not found'}), 404
        
        # Prepare data for LLM
        technique_data = {
            'technique_id': technique.technique_id,
            'name': technique.name,
            'description': technique.description,
            'tactic': technique.tactic,
            'platform': technique.platform
        }
        
        # Call LLM service
        analysis = llm_service.analyze_technique(technique_data)
        
        # Update technique with LLM results
        technique.llm_summary = analysis['summary']
        technique.llm_analysis = analysis['analysis']
        technique.llm_processed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'technique_id': technique_id,
            'summary': analysis['summary'],
            'analysis': analysis['analysis']
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the database"""
    total_techniques = AttackTechnique.query.count()
    total_tests = AtomicTest.query.count()
    analyzed_techniques = AttackTechnique.query.filter(
        AttackTechnique.llm_summary.isnot(None)
    ).count()
    
    return jsonify({
        'total_techniques': total_techniques,
        'total_tests': total_tests,
        'analyzed_techniques': analyzed_techniques,
        'analysis_percentage': round((analyzed_techniques / total_techniques * 100) if total_techniques > 0 else 0, 2)
    })


# Database initialization
@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def seed_db():
    """Seed the database with sample data"""
    # Create sample techniques
    sample_techniques = [
        {
            'technique_id': 'T1003',
            'name': 'OS Credential Dumping',
            'description': 'Adversaries may attempt to dump credentials to obtain account login information.',
            'tactic': 'Credential Access',
            'platform': 'Windows, Linux, macOS'
        },
        {
            'technique_id': 'T1059',
            'name': 'Command and Scripting Interpreter',
            'description': 'Adversaries may abuse command and script interpreters to execute commands.',
            'tactic': 'Execution',
            'platform': 'Windows, Linux, macOS'
        },
        {
            'technique_id': 'T1055',
            'name': 'Process Injection',
            'description': 'Adversaries may inject code into processes to evade detection.',
            'tactic': 'Defense Evasion, Privilege Escalation',
            'platform': 'Windows, Linux, macOS'
        }
    ]
    
    for tech_data in sample_techniques:
        technique = AttackTechnique.query.filter_by(
            technique_id=tech_data['technique_id']
        ).first()
        
        if not technique:
            technique = AttackTechnique(**tech_data)
            db.session.add(technique)
    
    db.session.commit()
    print('Database seeded!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Debug mode should be controlled by environment variable for security
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
