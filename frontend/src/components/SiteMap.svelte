<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let results = {};
  
  let svg;
  let width = 800;
  let height = 600;
  let simulation;
  let nodes = [];
  let links = [];

  $: {
    // Convert results to graph data whenever results change
    const graphData = processResults(results);
    nodes = graphData.nodes;
    links = graphData.links;
    updateSimulation();
  }

  function processResults(results) {
    const nodes = [];
    const links = [];
    const nodeMap = new Map();

    // Create nodes
    Object.keys(results).forEach(url => {
      if (!nodeMap.has(url)) {
        nodeMap.set(url, {
          id: url,
          label: new URL(url).pathname || '/',
          group: 1
        });
        nodes.push(nodeMap.get(url));
      }
    });

    // Create links
    Object.entries(results).forEach(([sourceUrl, targetUrls]) => {
      targetUrls.forEach(targetUrl => {
        if (!nodeMap.has(targetUrl)) {
          nodeMap.set(targetUrl, {
            id: targetUrl,
            label: new URL(targetUrl).pathname || '/',
            group: 1
          });
          nodes.push(nodeMap.get(targetUrl));
        }
        links.push({
          source: nodeMap.get(sourceUrl),
          target: nodeMap.get(targetUrl)
        });
      });
    });

    return { nodes, links };
  }

  function updateSimulation() {
    if (!svg) return;

    if (simulation) {
      simulation.stop();
    }

    simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .on('tick', ticked);

    const svgElement = d3.select(svg);
    svgElement.selectAll('*').remove();

    const link = svgElement.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 1);

    const node = svgElement.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g');

    node.append('circle')
      .attr('r', 5)
      .attr('fill', '#69b3a2');

    node.append('text')
      .text(d => d.label)
      .attr('x', 8)
      .attr('y', 4)
      .style('font-size', '10px');

    node.append('title')
      .text(d => d.id);

    function ticked() {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    }
  }
</script>

<div class="site-map">
  <svg bind:this={svg} {width} {height}></svg>
</div>

<style>
  .site-map {
    margin-top: 2rem;
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  svg {
    display: block;
    width: 100%;
    height: 600px;
  }
</style> 