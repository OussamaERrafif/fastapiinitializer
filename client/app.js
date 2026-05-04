let monacoEditor = null;
let allOptions = {};
let selectedDependencies = new Set(['pytest', 'docker', 'logging']);

const HISTORY_KEY = 'fastapi_generator_history';
const BOOKMARKS_KEY = 'fastapi_generator_bookmarks';
const MAX_HISTORY_ITEMS = 10;

// ── Utilities ─────────────────────────────────────────────────────────────────

function escapeHtml(text) {
    return text.replace(/[&<>"']/g, m =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m])
    );
}

// ── Toast notifications ───────────────────────────────────────────────────────

(function createToastContainer() {
    const el = document.createElement('div');
    el.className = 'toast-container';
    el.id = 'toast-container';
    document.body.appendChild(el);
})();

function showToast(message, type = 'info', durationMs = 4000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${escapeHtml(message)}</span>
        <button class="toast-dismiss" aria-label="Dismiss">×</button>
    `;

    const dismiss = () => {
        toast.style.animation = 'toastOut 0.2s ease forwards';
        toast.addEventListener('animationend', () => toast.remove(), { once: true });
    };

    toast.querySelector('.toast-dismiss').addEventListener('click', dismiss);
    container.appendChild(toast);
    setTimeout(dismiss, durationMs);
}

// ── Options loading ───────────────────────────────────────────────────────────

async function loadOptions() {
    try {
        const response = await fetch('/api/options');
        if (!response.ok) throw new Error(`Server returned ${response.status}`);
        allOptions = await response.json();
        populateTemplates();
        updateSelectedDepsDisplay();
        initMonaco();
    } catch (error) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = `Failed to load configuration options: ${error.message}. Please refresh the page.`;
        errorDiv.style.display = 'block';
    }
}

function initMonaco() {
    require.config({
        paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }
    });
    require(['vs/editor/editor.main'], function() {
        // Monaco is ready — nothing to log
    });
}

function populateTemplates() {
    const container = document.getElementById('templates-container');

    const iconMap = {
        'blank': 'document',
        'crud': 'document',
        'microservice': 'wrench',
        'monolith': 'building',
        'api-gateway': 'gateway'
    };

    allOptions.templates.forEach((template, index) => {
        const card = document.createElement('div');
        card.className = 'template-card';
        if (index === 0) card.classList.add('active');

        const iconId = iconMap[template.id] || 'document';

        card.innerHTML = `
            <input type="radio" id="template_${template.id}" name="template" value="${template.id}" ${index === 0 ? 'checked' : ''}>
            <div class="template-header">
                <div class="template-icon">
                    <svg class="icon-svg"><use href="#icon-${iconId}"/></svg>
                </div>
                <div class="template-name">${template.name}</div>
            </div>
            <div class="template-description">${template.description}</div>
        `;

        card.addEventListener('click', () => {
            document.querySelectorAll('.template-card').forEach(el => el.classList.remove('active'));
            card.classList.add('active');
            document.getElementById(`template_${template.id}`).checked = true;
        });

        container.appendChild(card);
    });
}

// ── Dependencies modal ───────────────────────────────────────────────────────

document.getElementById('add-deps-btn').addEventListener('click', () => {
    populateDepsModal();
    document.getElementById('deps-modal').classList.add('active');
});

document.getElementById('close-deps-modal').addEventListener('click', closeDepsModal);
document.getElementById('cancel-deps').addEventListener('click', closeDepsModal);

function closeDepsModal() {
    document.getElementById('deps-modal').classList.remove('active');
}

document.getElementById('save-deps').addEventListener('click', () => {
    updateSelectedDepsDisplay();
    closeDepsModal();
});

function populateDepsModal() {
    const container = document.getElementById('deps-modal-body');
    container.innerHTML = '';

    const categories = {};
    allOptions.dependencies.forEach(dep => {
        if (!categories[dep.category]) categories[dep.category] = [];
        categories[dep.category].push(dep);
    });

    Object.keys(categories).forEach(category => {
        const section = document.createElement('div');
        section.className = 'dep-category';

        const title = document.createElement('div');
        title.className = 'dep-category-title';
        title.textContent = category.charAt(0).toUpperCase() + category.slice(1);
        section.appendChild(title);

        const grid = document.createElement('div');
        grid.className = 'dep-grid';

        categories[category].forEach(dep => {
            const item = document.createElement('div');
            item.className = 'dep-item';
            if (selectedDependencies.has(dep.id)) item.classList.add('selected');

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `modal_dep_${dep.id}`;
            checkbox.value = dep.id;
            checkbox.checked = selectedDependencies.has(dep.id);

            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    selectedDependencies.add(dep.id);
                    item.classList.add('selected');
                } else {
                    selectedDependencies.delete(dep.id);
                    item.classList.remove('selected');
                }
            });

            const content = document.createElement('div');
            content.className = 'dep-item-content';
            content.innerHTML = `
                <div class="dep-item-name">${dep.name}</div>
                <div class="dep-item-desc">${dep.description}</div>
            `;

            item.appendChild(checkbox);
            item.appendChild(content);

            item.addEventListener('click', (e) => {
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });

            grid.appendChild(item);
        });

        section.appendChild(grid);
        container.appendChild(section);
    });
}

function updateSelectedDepsDisplay() {
    const container = document.getElementById('selected-deps');
    container.innerHTML = '';

    if (selectedDependencies.size === 0) {
        container.innerHTML = '<span class="empty-deps">No dependencies selected. Click "+ Add Dependencies" to select.</span>';
        return;
    }

    selectedDependencies.forEach(depId => {
        const dep = allOptions.dependencies.find(d => d.id === depId);
        if (dep) {
            const tag = document.createElement('div');
            tag.className = 'dep-tag';
            tag.innerHTML = `${dep.name}<span class="remove" data-dep="${depId}">×</span>`;
            tag.querySelector('.remove').addEventListener('click', () => {
                selectedDependencies.delete(depId);
                updateSelectedDepsDisplay();
            });
            container.appendChild(tag);
        }
    });
}

// ── Preview modal ────────────────────────────────────────────────────────────

document.getElementById('preview-btn').addEventListener('click', () => {
    generatePreview();
    document.getElementById('preview-modal').classList.add('active');
});

document.getElementById('close-preview-modal').addEventListener('click', closePreviewModal);
document.getElementById('close-preview').addEventListener('click', closePreviewModal);

function closePreviewModal() {
    document.getElementById('preview-modal').classList.remove('active');
    if (monacoEditor) {
        monacoEditor.dispose();
        monacoEditor = null;
    }
    document.getElementById('file-content-header').style.display = 'none';
    document.getElementById('file-content-empty').style.display = 'flex';
    document.getElementById('editor-container').classList.remove('active');
}

function generatePreview() {
    const config = getFormConfig();
    const tree = document.getElementById('file-tree');
    tree.innerHTML = '';
    renderFileTree(buildFileStructure(config), tree, 0);
}

function buildFileStructure(config) {
    const files = [{ name: config.project_name, type: 'folder', children: [
        { name: 'main.py', type: 'file' },
        { name: 'requirements.txt', type: 'file' },
        { name: 'README.md', type: 'file' },
        { name: '.gitignore', type: 'file' },
        { name: '.env.example', type: 'file' },
    ]}];

    const appFolder = { name: 'app', type: 'folder', children: [{ name: '__init__.py', type: 'file' }] };

    if (config.structure === 'standard') {
        appFolder.children.push({ name: 'api.py', type: 'file' }, { name: 'schemas.py', type: 'file' });
    } else if (config.structure === 'modular' || config.structure === 'microservice') {
        appFolder.children.push(
            { name: 'api', type: 'folder', children: [
                { name: '__init__.py', type: 'file' },
                { name: 'v1', type: 'folder', children: [
                    { name: '__init__.py', type: 'file' },
                    { name: 'endpoints.py', type: 'file' },
                ]}
            ]},
            { name: 'core', type: 'folder', children: [
                { name: '__init__.py', type: 'file' },
                { name: 'config.py', type: 'file' },
            ]}
        );
    }

    if (config.database !== 'none') appFolder.children.push({ name: 'database.py', type: 'file' });
    if (selectedDependencies.has('sqlalchemy')) appFolder.children.push({ name: 'models.py', type: 'file' });
    if (selectedDependencies.has('jwt') || selectedDependencies.has('oauth2')) appFolder.children.push({ name: 'auth.py', type: 'file' });
    if (selectedDependencies.has('celery')) appFolder.children.push({ name: 'celery_app.py', type: 'file' });
    if (config.include_middleware) appFolder.children.push({ name: 'middleware.py', type: 'file' });

    if (selectedDependencies.has('logging') || config.include_logging) {
        appFolder.children.push({ name: 'logging_config.py', type: 'file' });
        files[0].children.push({ name: 'logs', type: 'folder', children: [{ name: '.gitkeep', type: 'file' }] });
    }

    if (selectedDependencies.has('ratelimit')) appFolder.children.push({ name: 'rate_limiter.py', type: 'file' });

    files[0].children.push(appFolder);

    if (config.include_tests) {
        files[0].children.push({ name: 'tests', type: 'folder', children: [
            { name: '__init__.py', type: 'file' },
            { name: 'conftest.py', type: 'file' },
            { name: 'test_main.py', type: 'file' },
        ]});
    }

    if (selectedDependencies.has('docker') || config.include_docker) {
        files[0].children.push(
            { name: 'Dockerfile', type: 'file' },
            { name: 'docker-compose.yml', type: 'file' },
            { name: '.dockerignore', type: 'file' }
        );
    }

    if (config.ci_cd === 'github-actions') {
        files[0].children.push({ name: '.github', type: 'folder', children: [
            { name: 'workflows', type: 'folder', children: [{ name: 'ci.yml', type: 'file' }] }
        ]});
    } else if (config.ci_cd === 'gitlab-ci') {
        files[0].children.push({ name: '.gitlab-ci.yml', type: 'file' });
    }

    if (selectedDependencies.has('pre-commit')) {
        files[0].children.push({ name: '.pre-commit-config.yaml', type: 'file' });
    }

    return files;
}

function renderFileTree(items, container, level) {
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'file-tree-item ' + item.type;
        div.style.paddingLeft = `${level * 20}px`;

        const iconId = item.type === 'folder' ? 'folder' : 'file';
        const iconClass = item.type === 'folder' ? 'icon-svg-folder' : 'icon-svg-file';
        div.innerHTML = `<svg class="${iconClass}"><use href="#icon-${iconId}"/></svg> ${item.name}`;

        if (item.type === 'file') {
            div.addEventListener('click', () => {
                document.querySelectorAll('.file-tree-item.file').forEach(el => el.classList.remove('active'));
                div.classList.add('active');
                displayFileContent(item);
            });
        }

        container.appendChild(div);
        if (item.children) renderFileTree(item.children, container, level + 1);
    });
}

function displayFileContent(file) {
    const header = document.getElementById('file-content-header');
    const empty = document.getElementById('file-content-empty');
    const editorContainer = document.getElementById('editor-container');

    header.style.display = 'flex';
    empty.style.display = 'none';
    editorContainer.classList.add('active');
    document.getElementById('current-file-name').textContent = file.name;

    const fileContent = generateFileContent(file);
    const language = getLanguageFromFileName(file.name);

    if (!monacoEditor) {
        require(['vs/editor/editor.main'], function() {
            monacoEditor = monaco.editor.create(editorContainer, {
                value: fileContent,
                language: language,
                theme: 'vs-dark',
                readOnly: true,
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                fontSize: 13,
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                automaticLayout: true,
                folding: true,
                lineDecorationsWidth: 10,
                lineNumbersMinChars: 3,
                glyphMargin: false,
                scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10 }
            });
        });
    } else {
        monacoEditor.setModel(monaco.editor.createModel(fileContent, language));
    }
}

function getLanguageFromFileName(fileName) {
    if (fileName === 'Dockerfile') return 'dockerfile';
    if (fileName === '.gitignore' || fileName === '.dockerignore') return 'plaintext';
    if (fileName.startsWith('.env')) return 'plaintext';
    if (fileName === 'requirements.txt') return 'plaintext';

    const ext = fileName.split('.').pop().toLowerCase();
    return { py: 'python', js: 'javascript', ts: 'typescript', json: 'json',
             md: 'markdown', yml: 'yaml', yaml: 'yaml', sh: 'shell',
             toml: 'toml', ini: 'ini', cfg: 'ini' }[ext] || 'plaintext';
}

function generateFileContent(file) {
    const config = getFormConfig();
    const { name } = file;

    if (name === 'main.py') return generateMainPy(config);
    if (name === 'requirements.txt') return generateRequirements(config);
    if (name === 'README.md') return generateReadme(config);
    if (name === 'Dockerfile') return generateDockerfile(config);
    if (name === 'docker-compose.yml') return generateDockerCompose(config);
    if (name === '.env.example') return generateEnvExample(config);
    if (name === '.gitignore') return generateGitignore();
    if (name === 'ci.yml') return generateGitHubActions(config);
    if (name === '.gitlab-ci.yml') return generateGitLabCI(config);
    if (name.endsWith('.py')) return generatePythonFile(name, config);
    return `# ${name}\n\n# This file will be generated with appropriate content`;
}

function generateMainPy(config) {
    let content = `"""
${config.description || 'FastAPI Application'}
Author: ${config.author || 'Unknown'}
License: ${config.license}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
`;
    if (config.include_middleware) content += `from app.middleware import setup_middleware\n`;
    if (config.include_logging) content += `from app.logging_config import setup_logging\n\nsetup_logging()\n`;

    content += `
app = FastAPI(
    title="${config.project_name}",
    description="${config.description || 'A FastAPI application'}",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
`;
    if (config.include_middleware) content += `\nsetup_middleware(app)\n`;

    content += `
@app.get("/")
async def root():
    return {"message": "Welcome to ${config.project_name}", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
`;
    return content;
}

function generateRequirements(config) {
    let deps = ['fastapi>=0.104.0', 'uvicorn[standard]>=0.24.0', 'pydantic>=2.0.0', 'pydantic-settings>=2.0.0'];

    if (selectedDependencies.has('sqlalchemy')) deps.push('sqlalchemy>=2.0.0');
    if (selectedDependencies.has('tortoise')) deps.push('tortoise-orm>=0.20.0');
    if (selectedDependencies.has('alembic')) deps.push('alembic>=1.12.0');
    if (selectedDependencies.has('jwt')) deps.push('pyjwt>=2.8.0', 'python-jose[cryptography]>=3.3.0');
    if (selectedDependencies.has('oauth2')) deps.push('python-multipart>=0.0.6', 'passlib[bcrypt]>=1.7.4');
    if (selectedDependencies.has('celery')) deps.push('celery>=5.3.0');
    if (selectedDependencies.has('arq')) deps.push('arq>=0.25.0');
    if (selectedDependencies.has('redis')) deps.push('redis>=5.0.0');
    if (selectedDependencies.has('graphql')) deps.push('strawberry-graphql[fastapi]>=0.200.0');
    if (selectedDependencies.has('logging')) deps.push('loguru>=0.7.0');
    if (selectedDependencies.has('prometheus')) deps.push('prometheus-client>=0.18.0', 'prometheus-fastapi-instrumentator>=6.1.0');
    if (selectedDependencies.has('sentry')) deps.push('sentry-sdk[fastapi]>=1.38.0');
    if (selectedDependencies.has('ratelimit')) deps.push('slowapi>=0.1.9');
    if (selectedDependencies.has('pytest')) deps.push('pytest>=7.4.0', 'pytest-asyncio>=0.21.0', 'httpx>=0.25.0');
    if (selectedDependencies.has('pre-commit')) deps.push('pre-commit>=3.5.0');

    if (config.database === 'postgresql') deps.push('psycopg2-binary>=2.9.0');
    if (config.database === 'mysql') deps.push('pymysql>=1.1.0');
    if (config.database === 'mongodb') deps.push('motor>=3.3.0');

    return deps.sort().join('\n') + '\n';
}

function generateReadme(config) {
    return `# ${config.project_name}

${config.description || 'A FastAPI application'}

## Author
${config.author || 'Unknown'}

## License
${config.license}

## Quick Start

\`\`\`bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
\`\`\`

Visit http://localhost:8000/docs for API documentation.
`;
}

function generateDockerfile(config) {
    return `FROM python:${config.python_version}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
`;
}

function generateDockerCompose(config) {
    let compose = `version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=\${DATABASE_URL}
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --reload
`;
    if (config.database === 'postgresql') {
        compose += `
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ${config.project_name}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
`;
    }
    if (selectedDependencies.has('redis')) {
        compose += `
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
`;
    }
    if (config.database === 'postgresql' || selectedDependencies.has('redis')) {
        compose += `\nvolumes:`;
        if (config.database === 'postgresql') compose += `\n  postgres_data:`;
    }
    return compose;
}

function generateEnvExample(config) {
    let env = `APP_NAME=${config.project_name}\nENVIRONMENT=development\nDEBUG=True\n\nDATABASE_URL=sqlite:///./app.db\n`;
    if (selectedDependencies.has('jwt')) env += `\nSECRET_KEY=your-secret-key-here\nALGORITHM=HS256\n`;
    if (selectedDependencies.has('redis')) env += `\nREDIS_URL=redis://localhost:6379/0\n`;
    return env;
}

function generateGitignore() {
    return `__pycache__/\n*.py[cod]\n.Python\nenv/\nvenv/\n.venv\n*.egg-info/\n.env\n.env.local\n*.db\n*.sqlite\nlogs/\n*.log\n.DS_Store\n.pytest_cache/\n.coverage\nhtmlcov/\n`;
}

function generateGitHubActions(config) {
    return `name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '${config.python_version}'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest
`;
}

function generateGitLabCI(config) {
    return `stages:\n  - test\n\ntest:\n  stage: test\n  image: python:${config.python_version}\n  script:\n    - pip install -r requirements.txt\n    - pytest\n`;
}

function generatePythonFile(fileName, config) {
    if (fileName === '__init__.py') return '"""Application module"""';
    if (fileName === 'database.py') return `"""Database configuration"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
`;
    if (fileName === 'middleware.py') return `"""Custom middleware"""

from fastapi import Request
import time, uuid

async def request_id_middleware(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

def setup_middleware(app):
    app.middleware("http")(request_id_middleware)
`;
    return `"""${fileName}"""\n\n# File content will be generated`;
}

function getFormConfig() {
    const formData = new FormData(document.getElementById('generator-form'));
    const template = document.querySelector('input[name="template"]:checked').value;
    return {
        project_name: formData.get('project_name') || 'my_project',
        description: formData.get('description') || 'A FastAPI project',
        author: formData.get('author') || '',
        license: formData.get('license'),
        python_version: formData.get('python_version'),
        database: formData.get('database'),
        structure: formData.get('structure'),
        template: template,
        ci_cd: formData.get('ci_cd'),
        dependencies: Array.from(selectedDependencies),
        include_docker: formData.get('include_docker') === 'on',
        include_tests: formData.get('include_tests') === 'on',
        include_middleware: formData.get('include_middleware') === 'on',
        include_logging: formData.get('include_logging') === 'on',
    };
}

// ── Form submission ──────────────────────────────────────────────────────────

document.getElementById('generator-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const errorDiv = document.getElementById('error-message');
    errorDiv.style.display = 'none';

    const config = getFormConfig();
    document.getElementById('generate-btn').disabled = true;
    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || error.detail || 'Generation failed');
        }

        addToHistory(config);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${config.project_name}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.style.display = 'block';
    } finally {
        document.getElementById('generate-btn').disabled = false;
        document.getElementById('loading').style.display = 'none';
    }
});

// Close modals on background click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });
});

// ── History & Bookmarks ──────────────────────────────────────────────────────

function getHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
    catch (e) { return []; }
}

function saveHistory(history) {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(history)); }
    catch (e) { showToast('Could not save history — storage may be full or disabled.', 'warning'); }
}

function addToHistory(config) {
    const history = getHistory();
    history.unshift({ id: Date.now(), config, timestamp: new Date().toISOString(), projectName: config.project_name });
    if (history.length > MAX_HISTORY_ITEMS) history.pop();
    saveHistory(history);
    renderHistory();
}

function getBookmarks() {
    try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY) || '[]'); }
    catch (e) { return []; }
}

function saveBookmarks(bookmarks) {
    try { localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks)); }
    catch (e) { showToast('Could not save bookmark — storage may be full or disabled.', 'warning'); }
}

function addBookmark(name, config) {
    const bookmarks = getBookmarks();
    bookmarks.unshift({ id: Date.now(), name, config, timestamp: new Date().toISOString() });
    saveBookmarks(bookmarks);
    renderBookmarks();
}

function deleteBookmark(id) {
    saveBookmarks(getBookmarks().filter(b => b.id !== id));
    renderBookmarks();
}

function deleteHistoryItem(id) {
    saveHistory(getHistory().filter(h => h.id !== id));
    renderHistory();
}

function clearHistory() {
    saveHistory([]);
    renderHistory();
}

function loadConfig(config) {
    document.getElementById('project_name').value = config.project_name || '';
    document.getElementById('author').value = config.author || '';
    document.getElementById('description').value = config.description || '';
    document.getElementById('python_version').value = config.python_version || '3.11';
    document.getElementById('license').value = config.license || 'MIT';
    document.getElementById('structure').value = config.structure || 'standard';
    document.getElementById('database').value = config.database || 'sqlite';
    document.getElementById('ci_cd').value = config.ci_cd || 'github-actions';

    document.getElementById('include_docker').checked = config.include_docker !== false;
    document.getElementById('include_tests').checked = config.include_tests !== false;
    document.getElementById('include_middleware').checked = config.include_middleware !== false;
    document.getElementById('include_logging').checked = config.include_logging !== false;

    if (config.template) {
        const radio = document.getElementById(`template_${config.template}`);
        if (radio) {
            radio.checked = true;
            document.querySelectorAll('.template-card').forEach(el => el.classList.remove('active'));
            radio.closest('.template-card')?.classList.add('active');
        }
    }

    selectedDependencies.clear();
    (config.dependencies || []).forEach(dep => selectedDependencies.add(dep));
    updateSelectedDepsDisplay();

    document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const diff = Date.now() - date;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    return date.toLocaleDateString();
}

function renderHistory() {
    const container = document.getElementById('history-container');
    const history = getHistory();

    if (history.length === 0) {
        container.innerHTML = `<div class="empty-state"><svg><use href="#icon-history"/></svg><p>No history yet</p><p style="font-size:0.8em;">Generated projects will appear here</p></div>`;
        return;
    }

    container.innerHTML = history.map(item => `
        <div class="saved-item" data-id="${item.id}">
            <div class="saved-item-header">
                <span class="saved-item-name">${escapeHtml(item.projectName || 'Unnamed')}</span>
                <div class="saved-item-actions">
                    <button class="saved-item-btn bookmark" title="Save as bookmark" data-action="bookmark">
                        <svg class="icon-svg" style="width:14px;height:14px;"><use href="#icon-bookmark"/></svg>
                    </button>
                    <button class="saved-item-btn delete" title="Delete" data-action="delete">
                        <svg class="icon-svg" style="width:14px;height:14px;"><use href="#icon-trash"/></svg>
                    </button>
                </div>
            </div>
            <div class="saved-item-meta">
                <span>${item.config.structure || 'standard'}</span>
                <span>•</span>
                <span>${formatTimestamp(item.timestamp)}</span>
            </div>
        </div>
    `).join('');

    container.querySelectorAll('.saved-item').forEach(el => {
        const id = parseInt(el.dataset.id);
        const historyItem = history.find(h => h.id === id);

        el.addEventListener('click', (e) => {
            if (!e.target.closest('.saved-item-btn')) loadConfig(historyItem.config);
        });
        el.querySelector('[data-action="delete"]').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteHistoryItem(id);
        });
        el.querySelector('[data-action="bookmark"]').addEventListener('click', (e) => {
            e.stopPropagation();
            addBookmark(historyItem.projectName || 'Saved Config', historyItem.config);
            showBookmarkTab();
        });
    });
}

function renderBookmarks() {
    const container = document.getElementById('bookmarks-container');
    const bookmarks = getBookmarks();

    if (bookmarks.length === 0) {
        container.innerHTML = `<div class="empty-state"><svg><use href="#icon-bookmark"/></svg><p>No bookmarks yet</p><p style="font-size:0.8em;">Save your favorite configurations</p></div>`;
        return;
    }

    container.innerHTML = bookmarks.map(bookmark => `
        <div class="saved-item" data-id="${bookmark.id}">
            <div class="saved-item-header">
                <span class="saved-item-name">
                    <svg class="icon-svg" style="width:12px;height:12px;color:var(--warning);margin-right:4px;"><use href="#icon-bookmark-filled"/></svg>
                    ${escapeHtml(bookmark.name)}
                </span>
                <div class="saved-item-actions">
                    <button class="saved-item-btn delete" title="Delete" data-action="delete">
                        <svg class="icon-svg" style="width:14px;height:14px;"><use href="#icon-trash"/></svg>
                    </button>
                </div>
            </div>
            <div class="saved-item-meta">
                <span>${bookmark.config.project_name || 'unnamed'}</span>
                <span>•</span>
                <span>${bookmark.config.structure || 'standard'}</span>
            </div>
        </div>
    `).join('');

    container.querySelectorAll('.saved-item').forEach(el => {
        const id = parseInt(el.dataset.id);
        const bookmark = bookmarks.find(b => b.id === id);

        el.addEventListener('click', (e) => {
            if (!e.target.closest('.saved-item-btn')) loadConfig(bookmark.config);
        });
        el.querySelector('[data-action="delete"]').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteBookmark(id);
        });
    });
}

// ── Tabs ─────────────────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.getElementById(`${tab}-tab`).classList.add('active');
    });
});

function showBookmarkTab() {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('[data-tab="bookmarks"]').classList.add('active');
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById('bookmarks-tab').classList.add('active');
}

// ── Bookmark form ─────────────────────────────────────────────────────────────

document.getElementById('add-bookmark-btn').addEventListener('click', () => {
    const form = document.getElementById('bookmark-form');
    const input = document.getElementById('bookmark-name');
    form.classList.add('active');
    input.value = getFormConfig().project_name || 'My Config';
    input.focus();
    input.select();
});

document.getElementById('cancel-bookmark').addEventListener('click', () => {
    document.getElementById('bookmark-form').classList.remove('active');
});

document.getElementById('save-bookmark').addEventListener('click', () => {
    const name = document.getElementById('bookmark-name').value.trim();
    if (name) {
        addBookmark(name, getFormConfig());
        document.getElementById('bookmark-form').classList.remove('active');
    }
});

document.getElementById('bookmark-name').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); document.getElementById('save-bookmark').click(); }
    else if (e.key === 'Escape') { document.getElementById('bookmark-form').classList.remove('active'); }
});

document.getElementById('clear-history').addEventListener('click', () => {
    if (confirm('Are you sure you want to clear all history?')) clearHistory();
});

// ── Init ──────────────────────────────────────────────────────────────────────

loadOptions();
renderHistory();
renderBookmarks();
