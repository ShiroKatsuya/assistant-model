<div id="description" data-project-tabs-target="content" class="vertical-tabs__content" role="tabpanel" aria-labelledby="description-tab mobile-description-tab" tabindex="-1" style="display: block;" bis_skin_checked="1">
          <h2 class="page-title">Project description</h2>
          <div class="project-description" bis_skin_checked="1">
            <h1>Ollama Python Library</h1>
<p>The Ollama Python library provides the easiest way to integrate Python 3.8+ projects with <a href="https://github.com/ollama/ollama" rel="nofollow">Ollama</a>.</p>
<h2>Prerequisites</h2>
<ul>
<li><a href="https://ollama.com/download" rel="nofollow">Ollama</a> should be installed and running</li>
<li>Pull a model to use with the library: <code>ollama pull &lt;model&gt;</code> e.g. <code>ollama pull llama3.2</code>
<ul>
<li>See <a href="https://ollama.com/search" rel="nofollow">Ollama.com</a> for more information on the models available.</li>
</ul>
</li>
</ul>
<h2>Install</h2>
<pre lang="sh">pip<span class="w"> </span>install<span class="w"> </span>ollama
</pre>
<h2>Usage</h2>
<pre lang="python3"><span class="kn">from</span> <span class="nn">ollama</span> <span class="kn">import</span> <span class="n">chat</span>
<span class="kn">from</span> <span class="nn">ollama</span> <span class="kn">import</span> <span class="n">ChatResponse</span>

<span class="n">response</span><span class="p">:</span> <span class="n">ChatResponse</span> <span class="o">=</span> <span class="n">chat</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="n">messages</span><span class="o">=</span><span class="p">[</span>
  <span class="p">{</span>
    <span class="s1">'role'</span><span class="p">:</span> <span class="s1">'user'</span><span class="p">,</span>
    <span class="s1">'content'</span><span class="p">:</span> <span class="s1">'Why is the sky blue?'</span><span class="p">,</span>
  <span class="p">},</span>
<span class="p">])</span>
<span class="nb">print</span><span class="p">(</span><span class="n">response</span><span class="p">[</span><span class="s1">'message'</span><span class="p">][</span><span class="s1">'content'</span><span class="p">])</span>
<span class="c1"># or access fields directly from the response object</span>
<span class="nb">print</span><span class="p">(</span><span class="n">response</span><span class="o">.</span><span class="n">message</span><span class="o">.</span><span class="n">content</span><span class="p">)</span>
</pre>
<p>See <a href="ollama/_types.py" rel="nofollow">_types.py</a> for more information on the response types.</p>
<h2>Streaming responses</h2>
<p>Response streaming can be enabled by setting <code>stream=True</code>.</p>
<blockquote>
<p>[!NOTE]
Streaming Tool/Function calling is not yet supported.</p>
</blockquote>
<pre lang="python3"><span class="kn">from</span> <span class="nn">ollama</span> <span class="kn">import</span> <span class="n">chat</span>

<span class="n">stream</span> <span class="o">=</span> <span class="n">chat</span><span class="p">(</span>
    <span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span>
    <span class="n">messages</span><span class="o">=</span><span class="p">[{</span><span class="s1">'role'</span><span class="p">:</span> <span class="s1">'user'</span><span class="p">,</span> <span class="s1">'content'</span><span class="p">:</span> <span class="s1">'Why is the sky blue?'</span><span class="p">}],</span>
    <span class="n">stream</span><span class="o">=</span><span class="kc">True</span><span class="p">,</span>
<span class="p">)</span>

<span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">stream</span><span class="p">:</span>
  <span class="nb">print</span><span class="p">(</span><span class="n">chunk</span><span class="p">[</span><span class="s1">'message'</span><span class="p">][</span><span class="s1">'content'</span><span class="p">],</span> <span class="n">end</span><span class="o">=</span><span class="s1">''</span><span class="p">,</span> <span class="n">flush</span><span class="o">=</span><span class="kc">True</span><span class="p">)</span>
</pre>
<h2>Custom client</h2>
<p>A custom client can be created by instantiating <code>Client</code> or <code>AsyncClient</code> from <code>ollama</code>.</p>
<p>All extra keyword arguments are passed into the <a href="https://www.python-httpx.org/api/#client" rel="nofollow"><code>httpx.Client</code></a>.</p>
<pre lang="python3"><span class="kn">from</span> <span class="nn">ollama</span> <span class="kn">import</span> <span class="n">Client</span>
<span class="n">client</span> <span class="o">=</span> <span class="n">Client</span><span class="p">(</span>
  <span class="n">host</span><span class="o">=</span><span class="s1">'http://localhost:11434'</span><span class="p">,</span>
  <span class="n">headers</span><span class="o">=</span><span class="p">{</span><span class="s1">'x-some-header'</span><span class="p">:</span> <span class="s1">'some-value'</span><span class="p">}</span>
<span class="p">)</span>
<span class="n">response</span> <span class="o">=</span> <span class="n">client</span><span class="o">.</span><span class="n">chat</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="n">messages</span><span class="o">=</span><span class="p">[</span>
  <span class="p">{</span>
    <span class="s1">'role'</span><span class="p">:</span> <span class="s1">'user'</span><span class="p">,</span>
    <span class="s1">'content'</span><span class="p">:</span> <span class="s1">'Why is the sky blue?'</span><span class="p">,</span>
  <span class="p">},</span>
<span class="p">])</span>
</pre>
<h2>Async client</h2>
<p>The <code>AsyncClient</code> class is used to make asynchronous requests. It can be configured with the same fields as the <code>Client</code> class.</p>
<pre lang="python3"><span class="kn">import</span> <span class="nn">asyncio</span>
<span class="kn">from</span> <span class="nn">ollama</span> <span class="kn">import</span> <span class="n">AsyncClient</span>

<span class="k">async</span> <span class="k">def</span> <span class="nf">chat</span><span class="p">():</span>
  <span class="n">message</span> <span class="o">=</span> <span class="p">{</span><span class="s1">'role'</span><span class="p">:</span> <span class="s1">'user'</span><span class="p">,</span> <span class="s1">'content'</span><span class="p">:</span> <span class="s1">'Why is the sky blue?'</span><span class="p">}</span>
  <span class="n">response</span> <span class="o">=</span> <span class="k">await</span> <span class="n">AsyncClient</span><span class="p">()</span><span class="o">.</span><span class="n">chat</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="n">messages</span><span class="o">=</span><span class="p">[</span><span class="n">message</span><span class="p">])</span>

<span class="n">asyncio</span><span class="o">.</span><span class="n">run</span><span class="p">(</span><span class="n">chat</span><span class="p">())</span>
</pre>
<p>Setting <code>stream=True</code> modifies functions to return a Python asynchronous generator:</p>
<pre lang="python3"><span class="kn">import</span> <span class="nn">asyncio</span>
<span class="kn">from</span> <span class="nn">ollama</span> <span class="kn">import</span> <span class="n">AsyncClient</span>

<span class="k">async</span> <span class="k">def</span> <span class="nf">chat</span><span class="p">():</span>
  <span class="n">message</span> <span class="o">=</span> <span class="p">{</span><span class="s1">'role'</span><span class="p">:</span> <span class="s1">'user'</span><span class="p">,</span> <span class="s1">'content'</span><span class="p">:</span> <span class="s1">'Why is the sky blue?'</span><span class="p">}</span>
  <span class="k">async</span> <span class="k">for</span> <span class="n">part</span> <span class="ow">in</span> <span class="k">await</span> <span class="n">AsyncClient</span><span class="p">()</span><span class="o">.</span><span class="n">chat</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="n">messages</span><span class="o">=</span><span class="p">[</span><span class="n">message</span><span class="p">],</span> <span class="n">stream</span><span class="o">=</span><span class="kc">True</span><span class="p">):</span>
    <span class="nb">print</span><span class="p">(</span><span class="n">part</span><span class="p">[</span><span class="s1">'message'</span><span class="p">][</span><span class="s1">'content'</span><span class="p">],</span> <span class="n">end</span><span class="o">=</span><span class="s1">''</span><span class="p">,</span> <span class="n">flush</span><span class="o">=</span><span class="kc">True</span><span class="p">)</span>

<span class="n">asyncio</span><span class="o">.</span><span class="n">run</span><span class="p">(</span><span class="n">chat</span><span class="p">())</span>
</pre>
<h2>API</h2>
<p>The Ollama Python library's API is designed around the <a href="https://github.com/ollama/ollama/blob/main/docs/api.md" rel="nofollow">Ollama REST API</a></p>
<h3>Chat</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">chat</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="n">messages</span><span class="o">=</span><span class="p">[{</span><span class="s1">'role'</span><span class="p">:</span> <span class="s1">'user'</span><span class="p">,</span> <span class="s1">'content'</span><span class="p">:</span> <span class="s1">'Why is the sky blue?'</span><span class="p">}])</span>
</pre>
<h3>Generate</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">generate</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="n">prompt</span><span class="o">=</span><span class="s1">'Why is the sky blue?'</span><span class="p">)</span>
</pre>
<h3>List</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">list</span><span class="p">()</span>
</pre>
<h3>Show</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">show</span><span class="p">(</span><span class="s1">'llama3.2'</span><span class="p">)</span>
</pre>
<h3>Create</h3>
<pre lang="python3"><span class="n">modelfile</span><span class="o">=</span><span class="s1">'''</span>
<span class="s1">FROM llama3.2</span>
<span class="s1">SYSTEM You are mario from super mario bros.</span>
<span class="s1">'''</span>

<span class="n">ollama</span><span class="o">.</span><span class="n">create</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'example'</span><span class="p">,</span> <span class="n">modelfile</span><span class="o">=</span><span class="n">modelfile</span><span class="p">)</span>
</pre>
<h3>Copy</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">copy</span><span class="p">(</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="s1">'user/llama3.2'</span><span class="p">)</span>
</pre>
<h3>Delete</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">delete</span><span class="p">(</span><span class="s1">'llama3.2'</span><span class="p">)</span>
</pre>
<h3>Pull</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">pull</span><span class="p">(</span><span class="s1">'llama3.2'</span><span class="p">)</span>
</pre>
<h3>Push</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">push</span><span class="p">(</span><span class="s1">'user/llama3.2'</span><span class="p">)</span>
</pre>
<h3>Embed</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">embed</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="nb">input</span><span class="o">=</span><span class="s1">'The sky is blue because of rayleigh scattering'</span><span class="p">)</span>
</pre>
<h3>Embed (batch)</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">embed</span><span class="p">(</span><span class="n">model</span><span class="o">=</span><span class="s1">'llama3.2'</span><span class="p">,</span> <span class="nb">input</span><span class="o">=</span><span class="p">[</span><span class="s1">'The sky is blue because of rayleigh scattering'</span><span class="p">,</span> <span class="s1">'Grass is green because of chlorophyll'</span><span class="p">])</span>
</pre>
<h3>Ps</h3>
<pre lang="python3"><span class="n">ollama</span><span class="o">.</span><span class="n">ps</span><span class="p">()</span>
</pre>
<h2>Errors</h2>
<p>Errors are raised if requests return an error status or if an error is detected while streaming.</p>
<pre lang="python3"><span class="n">model</span> <span class="o">=</span> <span class="s1">'does-not-yet-exist'</span>

<span class="k">try</span><span class="p">:</span>
  <span class="n">ollama</span><span class="o">.</span><span class="n">chat</span><span class="p">(</span><span class="n">model</span><span class="p">)</span>
<span class="k">except</span> <span class="n">ollama</span><span class="o">.</span><span class="n">ResponseError</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
  <span class="nb">print</span><span class="p">(</span><span class="s1">'Error:'</span><span class="p">,</span> <span class="n">e</span><span class="o">.</span><span class="n">error</span><span class="p">)</span>
  <span class="k">if</span> <span class="n">e</span><span class="o">.</span><span class="n">status_code</span> <span class="o">==</span> <span class="mi">404</span><span class="p">:</span>
    <span class="n">ollama</span><span class="o">.</span><span class="n">pull</span><span class="p">(</span><span class="n">model</span><span class="p">)</span>
</pre>


