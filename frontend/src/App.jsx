import { useState, useEffect } from 'react';
import ReactFlow, { Controls, Background } from 'reactflow';
import 'reactflow/dist/style.css';
import { 
  Play, 
  Loader2, 
  CheckCircle, 
  Copy, 
  Check, 
  Activity, 
  Sparkles,
  HelpCircle,
  FileText
} from 'lucide-react';

const initialNodes = [
  { id: 'user', data: { label: '👤 User Query' }, position: { x: 400, y: 50 } },
  { id: 'planner', data: { label: '📋 Planner' }, position: { x: 400, y: 160 } },
  { id: 'orchestrator', data: { label: '🎯 Orchestrator' }, position: { x: 400, y: 270 } },
  { id: 'search1', data: { label: '🔍 Searcher 1' }, position: { x: 100, y: 400 } },
  { id: 'search2', data: { label: '🔍 Searcher 2' }, position: { x: 280, y: 400 } },
  { id: 'search3', data: { label: '🔍 Searcher 3' }, position: { x: 460, y: 400 } },
  { id: 'critic', data: { label: '🔬 Critic' }, position: { x: 280, y: 530 } },
  { id: 'factchecker', data: { label: '✅ Fact-Checker' }, position: { x: 520, y: 530 } },
  { id: 'synthesizer', data: { label: '📝 Synthesizer' }, position: { x: 400, y: 650 } },
  { id: 'final', data: { label: '📄 Final Report' }, position: { x: 400, y: 770 } },
];

const initialEdges = [
  { id: 'e1', source: 'user', target: 'planner' },
  { id: 'e2', source: 'planner', target: 'orchestrator' },
  { id: 'e3', source: 'orchestrator', target: 'search1' },
  { id: 'e4', source: 'orchestrator', target: 'search2' },
  { id: 'e5', source: 'orchestrator', target: 'search3' },
  { id: 'e7', source: 'search1', target: 'critic' },
  { id: 'e8', source: 'search2', target: 'critic' },
  { id: 'e9', source: 'search3', target: 'critic' },
  { id: 'e11', source: 'critic', target: 'factchecker' },
  { id: 'e12', source: 'factchecker', target: 'synthesizer' },
  { id: 'e13', source: 'synthesizer', target: 'final' },
];

// Simple custom Markdown parser to avoid external dependencies
const parseMarkdown = (markdown) => {
  if (!markdown) return "";
  
  // Escape HTML tags to prevent XSS
  let html = markdown
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold text: **text**
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Code blocks: ```code```
  html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

  // Inline code: `code`
  html = html.replace(/`(.*?)`/g, "<code>$1</code>");

  // Headings: ### Title, ## Title, # Title
  html = html.replace(/^### (.*?)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.*?)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.*?)$/gm, "<h1>$1</h1>");

  // Bullet lists: - item or * item
  html = html.replace(/^\s*[-*]\s+(.*?)$/gm, "<li>$1</li>");

  // Links: [Text](Url)
  html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: #a78bfa; text-decoration: underline;">$1</a>');

  // Handle double newlines for paragraphs
  html = html.replace(/\n\n/g, "</p><p>");
  // Single newlines for line breaks
  html = html.replace(/\n/g, "<br />");

  return `<p>${html}</p>`;
};

export default function App() {
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [report, setReport] = useState("");
  const [activeNode, setActiveNode] = useState("idle");
  const [status, setStatus] = useState("idle");
  const [copied, setCopied] = useState(false);
  
  // State from checkpointer
  const [subQuestions, setSubQuestions] = useState([]);
  const [findingsCount, setFindingsCount] = useState(0);
  const [criticRounds, setCriticRounds] = useState(0);
  const [error, setError] = useState("");

  const handleCopy = () => {
    if (!report) return;
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsProcessing(true);
    setReport("");
    setActiveNode("planner");
    setStatus("in_progress");
    setSubQuestions([]);
    setFindingsCount(0);
    setCriticRounds(0);
    setError("");

    try {
      // 1. Start the research session in the background
      const res = await fetch('http://127.0.0.1:8000/api/v1/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      if (!res.ok) {
        throw new Error("Failed to start research session");
      }

      const startData = await res.json();
      const session_id = startData.session_id;

      // 2. Poll for session state
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`http://127.0.0.1:8000/api/v1/research/${session_id}`);
          if (!statusRes.ok) return;

          const statusData = await statusRes.json();
          
          setStatus(statusData.status);
          setActiveNode(statusData.active_node || "planner");
          setSubQuestions(statusData.sub_questions || []);
          setFindingsCount(statusData.findings_count || 0);
          setCriticRounds(statusData.critic_rounds || 0);

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            setIsProcessing(false);
            setReport(statusData.final_report || "Research complete. No report was generated.");
            setActiveNode("final");
          } else if (statusData.status === 'error' || statusData.status === 'failed') {
            clearInterval(pollInterval);
            setIsProcessing(false);
            setError(statusData.message || "Research session failed.");
            setActiveNode("idle");
          }
        } catch (pollErr) {
          console.error("Error polling research status:", pollErr);
        }
      }, 1500);

    } catch (err) {
      setError(err.message || "Error connecting to backend.");
      setIsProcessing(false);
      setActiveNode("idle");
      setStatus("idle");
    }
  };

  // Node highlighting lookup
  const nodeMapping = {
    user: { active: false, completed: true },
    planner: { active: activeNode === 'planner', completed: ['orchestrator', 'searcher', 'critic', 'fact_checker', 'synthesizer', 'final'].includes(activeNode) },
    orchestrator: { active: activeNode === 'orchestrator', completed: ['searcher', 'critic', 'fact_checker', 'synthesizer', 'final'].includes(activeNode) },
    search1: { active: activeNode === 'searcher', completed: ['critic', 'fact_checker', 'synthesizer', 'final'].includes(activeNode) },
    search2: { active: activeNode === 'searcher', completed: ['critic', 'fact_checker', 'synthesizer', 'final'].includes(activeNode) },
    search3: { active: activeNode === 'searcher', completed: ['critic', 'fact_checker', 'synthesizer', 'final'].includes(activeNode) },
    critic: { active: activeNode === 'critic', completed: ['fact_checker', 'synthesizer', 'final'].includes(activeNode) },
    factchecker: { active: activeNode === 'fact_checker', completed: ['synthesizer', 'final'].includes(activeNode) },
    synthesizer: { active: activeNode === 'synthesizer', completed: ['final'].includes(activeNode) },
    final: { active: activeNode === 'final', completed: status === 'completed' }
  };

  const nodes = initialNodes.map(node => {
    const mapVal = nodeMapping[node.id];
    let className = '';
    if (mapVal) {
      if (mapVal.active) {
        className = 'active-swarm-node' + (['search1', 'search2', 'search3'].includes(node.id) ? ' pulse-node' : '');
      } else if (mapVal.completed) {
        className = 'completed-swarm-node';
      }
    }
    return {
      ...node,
      className,
      style: undefined
    };
  });

  const edges = initialEdges.map(edge => {
    const isTargetActive = nodeMapping[edge.target]?.active;
    const isTargetCompleted = nodeMapping[edge.target]?.completed;
    return {
      ...edge,
      className: isTargetActive ? 'active-swarm-edge' : '',
      animated: isTargetActive || (isProcessing && isTargetCompleted)
    };
  });

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">Deep Research Agent Swarm</h1>
        <p className="app-subtitle">Multi-Agent Deep Intelligence Search</p>
      </header>

      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-container">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search US/Indian Stock Markets or analyze complex topics..."
            className="search-input"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !query.trim()}
            className="submit-btn"
          >
            {isProcessing ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
            Start Research
          </button>
        </div>
      </form>

      <div className="dashboard-grid">
        {/* Swarm Visualizer Panel */}
        <div className="panel flow-panel">
          <h3 className="panel-title">
            <Sparkles size={20} className="text-violet-400" /> Swarm Execution Path
          </h3>
          <div className="react-flow-wrapper">
            <ReactFlow nodes={nodes} edges={edges} fitView>
              <Background color="#1e293b" gap={16} size={1} />
              <Controls />
            </ReactFlow>
          </div>
        </div>

        {/* Live Status and Output Panel */}
        <div className="panel output-panel">
          <h3 className="panel-title">
            <Activity size={20} className={isProcessing ? "animate-pulse text-violet-400" : "text-green-400"} /> 
            Live Swarm Monitor
          </h3>

          {/* Stats bar */}
          <div className="stats-header">
            <div className="stat-card">
              <div className="stat-label">Status</div>
              <div className={`stat-value status-badge ${status === 'completed' ? 'completed' : isProcessing ? 'active' : 'idle'}`}>
                {status === 'completed' ? 'Done' : isProcessing ? 'Running' : 'Idle'}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Sub-Questions</div>
              <div className="stat-value">{subQuestions.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Findings</div>
              <div className="stat-value">{findingsCount}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Critic Rounds</div>
              <div className="stat-value">{criticRounds}</div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{ color: '#ef4444', background: 'rgba(239, 68, 68, 0.1)', padding: '12px', borderRadius: '10px', marginBottom: '16px', border: '1px solid rgba(239, 68, 68, 0.2)', fontSize: '0.9rem' }}>
              ⚠️ {error}
            </div>
          )}

          {/* Sub questions log */}
          {subQuestions.length > 0 && !report && (
            <div style={{ marginBottom: '24px' }}>
              <div className="stat-label" style={{ textAlign: 'left', marginBottom: '8px' }}>Active Sub-Questions:</div>
              <div className="sub-qs-list">
                {subQuestions.map((q) => (
                  <div key={q.id} className="sub-q-item">
                    <span>{q.question}</span>
                    <span className={`sub-q-badge ${q.status === 'done' ? 'done' : 'pending'}`}>
                      {q.status === 'done' ? 'Checked' : 'Searching'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Report Display */}
          <div className="report-container">
            {report ? (
              <>
                <div className="report-actions">
                  <span className="stat-label"><FileText size={14} style={{ marginRight: '4px', verticalAlign: 'middle' }} /> Research Report:</span>
                  <button onClick={handleCopy} className="copy-btn">
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                    {copied ? 'Copied' : 'Copy Report'}
                  </button>
                </div>
                <div 
                  className="report-markdown"
                  dangerouslySetInnerHTML={{ __html: parseMarkdown(report) }}
                />
              </>
            ) : isProcessing ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '240px', color: '#9ca3af', gap: '16px' }}>
                <Loader2 className="animate-spin text-violet-400" size={36} />
                <p style={{ fontStyle: 'italic', fontSize: '0.95rem' }}>Swarm agents are researching the web and compiling evidence...</p>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '240px', color: '#6b7280', fontStyle: 'italic', fontSize: '0.95rem' }}>
                Submit a query to coordinate the multi-agent search...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}