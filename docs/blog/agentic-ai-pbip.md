# How I Built a Power BI Tool with AI (Dublin Demo)

Last week at the Dublin Fabric User Group, I showed how Power BI Projects (PBIP) unlocks AI-assisted development in ways .pbix files never could.

The takeaway: **You cannot afford to wait.**

## Text-Based Models Change Everything

PBIP saves your semantic models as text files—tables, relationships, measures. That metadata locked inside binary .pbix files? Now it's readable Tabular Model Definition Language (TMDL).

This matters because AI can't work with what it can't read. 

.pbix files? AI is blind. Text files? AI becomes your development partner—reading your schema, understanding relationships, building tools to analyze and automate.

This isn't theoretical. I built a tool live during the session.

## Building Tools Through Conversation

I wanted a good demo for the session—something that showed what's possible with AI and PBIP. Before the meetup, I spent about 10 minutes building the tool with Copilot, refining prompts until I had exactly what I needed. Another 10 minutes to document the process.

I captured both approaches in the [building tools with AI tutorial](../tutorials/building-tools-with-ai.md):
- **Iterative approach**: 6 progressive prompts, each adding features (interactive HTML, multi-model dropdown, table filtering)
- **One-shot approach**: Single comprehensive prompt for time-constrained demos

During the live session, I used the one-shot prompt (time got a little tight, otherwise I would have done the iterative version). One minute, one request: build a Python script that scans for TMDL files, parses relationships, and generates an interactive HTML visualization with filtering, legends, and CLI arguments.

Copilot delivered a production-ready relationship visualizer—the kind of thing that normally takes hours or that you skip because the effort isn't worth it.

**This only works because PBIP gave AI something to read.**

## Model Context Protocol: The Next Step

AI integration is evolving fast. First, you ask ChatGPT questions in a browser—helpful but disconnected. Then AI moves into your dev environment—Copilot in VS Code, creating files and modifying your project.

Next: **Model Context Protocol (MCP)**. This gives agentic AI structured access to tools—your dev environment, your data, your workflows. Microsoft just released an MCP for Power BI modeling.

Instead of just generating code, AI can interact with your semantic models directly: run best practice analysis, apply fixes, generate documentation, all through structured tool access.

**PBIP is the foundation for this.** 

Without text-based models, AI stays stuck answering questions. With PBIP, AI becomes a partner that reads your models, understands them, and uses tools to transform them. Not convenience—capability.

## What This Opens Up

PBIP + agentic AI:

- Build custom analysis tools by describing what you want
- Automate quality checks against your models
- Generate documentation from your metadata
- Visualize model complexity
- Implement CI/CD with quality gates
- Get help refactoring and optimizing complex DAX

You're not learning to code. You're learning to articulate problems. AI handles implementation.

## Try It Yourself

The relationship viewer tool and prompts:

- **Tool**: `visualize_all_relationships.py` - Production-ready, portable script
- **README**: Complete usage guide in [Tools section](../tools/relationship-viewer.md)
- **Demo Guide**: Step-by-step prompts in [Tutorials](../tutorials/building-tools-with-ai.md)

### What Makes This Tool Interesting

Not a static diagram generator—an interactive analysis tool built by describing the problem to AI:

**🔍 Full Repository Visibility**
- Scans your entire repo recursively, finds all `.SemanticModel` folders
- Multi-model dropdown—analyze any model from one HTML file
- No manual configuration, just point it at your repo

**🎯 Interactive Filtering**
- **Model Selector**: Switch between models via dropdown
- **Table Filter Panel**: Show/hide tables to focus on complex model sections
- Classifies fact vs. dimension tables based on relationship patterns

**🔗 Relationship Visualization Modes**
- **All Relations Mode**: Click a table to see all its direct relationships highlighted
- **Filter Direction Mode**: Visualizes transitive filter propagation—see the entire chain of tables filtered by your selection
- Toggle between modes to understand different aspects of your model's behavior

**📊 Visual Design**
- Fact tables (red boxes) vs. dimensions (teal circles)
- Bidirectional relationships in purple with wider lines
- Inactive relationships as dashed lines
- Hover tooltips show cardinality and column mappings

**🎨 Production-Ready Output**
- Self-contained HTML (500KB-2MB), zero external dependencies
- Works offline, shareable with stakeholders, integrates into CI/CD
- Interactive physics-based graph—zoom, pan, explore

### Quick Start

```bash
python visualize_all_relationships.py
```

## The Point Wasn't the Tool

The relationship viewer is useful, but that's not the point.

**PBIP + AI changes the equation.** Problems too small to justify the effort become trivial. Ideas you never acted on because "it would take too long" are afternoon projects.

Your metadata was always valuable. PBIP makes it accessible. AI makes it actionable.

## Start Now

Still using .pbix exclusively? You're working with one hand tied behind your back. Move to PBIP. Enable Copilot or Claude. Start experimenting.

The tools you build will fit your needs because you're directing AI based on your problems, not searching for generic solutions.

You cannot afford to wait. The technology is here, and it's transforming Power BI development.

## Thank You, Dublin

Thanks to the Dublin Fabric User Group and everyone who attended. The questions were fantastic.

If you build something with PBIP + AI, let me know. The future of BI development is conversational, and it's already here.

---

**Resources:**
- [Tool Documentation](../tools/relationship-viewer.md)
- [Tutorial: Building Tools with AI](../tutorials/building-tools-with-ai.md)
- [Scripts Folder](https://github.com/JoeRossouw/semantic_ops/tree/main/scripts)

**Connect:**  
Have questions or want to share what you've built? Open an issue or reach out!
