<script>
  import { onMount, onDestroy } from 'svelte';
  import { select } from 'd3-selection';
  import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force';
  import { zoom } from 'd3-zoom';
  import { drag } from 'd3-drag';
  import { interpolateBlues } from 'd3-scale-chromatic';
  import { throttle } from 'lodash-es';

  export let results = {};
  
  let container;
  let svg;
  let width;
  let height;
  let simulation;
  let nodes = [];
  let links = [];
  let zoomBehavior;
  const MAX_VISIBLE_NODES = 100; // Limit visible nodes
  let isProcessing = false;
  let isInitialized = false;

  // Initialize dimensions and setup
  function initialize() {
    if (!container || !svg || isInitialized) return;
    
    width = container.offsetWidth;
    height = Math.max(600, window.innerHeight * 0.6);
    
    select(svg)
      .attr('width', width)
      .attr('height', height);

    // Initialize zoom behavior
    zoomBehavior = zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        select(svg).select('g.zoom-group')
          .attr('transform', event.transform);
      });

    // Add zoom behavior to SVG
    select(svg).call(zoomBehavior);
    
    isInitialized = true;
  }

  // Throttle the update function
  const throttledUpdate = throttle((newResults) => {
    if (Object.keys(newResults).length > 0) {
      const graphData = processResults(newResults);
      nodes = graphData.nodes;
      links = graphData.links;
      updateSimulation(true);
    }
  }, 1000);

  // Watch for changes in results
  $: {
    if (!isProcessing && Object.keys(results).length > 0) {
      isProcessing = true;
      initialize();
      throttledUpdate(results);
      isProcessing = false;
    }
  }

  function processResults(results) {
    const nodes = [];
    const links = [];
    const nodeMap = new Map();
    
    // Sort URLs by importance (root URLs first)
    const sortedUrls = Object.keys(results).sort((a, b) => {
      const depthA = (a.match(/\//g) || []).length;
      const depthB = (b.match(/\//g) || []).length;
      return depthA - depthB;
    });

    // Limit the number of nodes if necessary
    const limitedUrls = sortedUrls.slice(0, MAX_VISIBLE_NODES);

    // Create nodes
    limitedUrls.forEach(url => {
      if (!nodeMap.has(url)) {
        nodeMap.set(url, {
          id: url,
          label: truncateUrl(url),
          group: 1,
          depth: (url.match(/\//g) || []).length
        });
        nodes.push(nodeMap.get(url));
      }
    });

    // Create links only for visible nodes
    limitedUrls.forEach(sourceUrl => {
      const targetUrls = results[sourceUrl] || [];
      targetUrls.forEach(targetUrl => {
        if (nodeMap.has(targetUrl) && links.length < MAX_VISIBLE_NODES * 2) {
          links.push({
            source: nodeMap.get(sourceUrl),
            target: nodeMap.get(targetUrl)
          });
        }
      });
    });


    return { nodes, links };
  }

  function truncateUrl(url) {
    try {
      const urlObj = new URL(url);
      const path = urlObj.pathname;
      if (path.length > 30) {
        return path.substring(0, 15) + '...' + path.substring(path.length - 15);
      }
      return path || '/';
    } catch (e) {
      return url;
    }
  }

  function updateSimulation(isNewData = false) {
    console.log('Updating simulation:', { isNewData, nodes: nodes.length, links: links.length });
    if (!svg || !width || !height) {
      console.log('Missing required elements:', { svg: !!svg, width, height });
      return;
    }

    if (simulation) {
      simulation.stop();
    }

    const coolingFactor = Math.max(0.0001, 0.01 - (nodes.length / 1000));

    simulation = forceSimulation(nodes)
      .force('link', forceLink(links)
        .id(d => d.id)
        .distance(d => 100 + d.source.depth * 20)
        .strength(0.5))
      .force('charge', forceManyBody()
        .strength(d => -300 - d.depth * 50)
        .distanceMax(350))
      .force('collision', forceCollide().radius(30))
      .force('center', forceCenter(width / 2, height / 2))
      .alphaDecay(coolingFactor)
      .velocityDecay(0.4)
      .on('tick', throttle(ticked, 50));

    const svgElement = select(svg);
    
    if (isNewData) {
      svgElement.selectAll('*').remove();
      
      // Create zoom container
      const zoomGroup = svgElement
        .append('g')
        .attr('class', 'zoom-group');

      // Add warning message if nodes were limited
      if (Object.keys(results).length > MAX_VISIBLE_NODES) {
        svgElement
          .append('text')
          .attr('class', 'warning-text')
          .attr('x', 10)
          .attr('y', 20)
          .text(`Showing ${MAX_VISIBLE_NODES} of ${Object.keys(results).length} nodes`);
      }

      // Create arrow marker
      zoomGroup.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '-0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('orient', 'auto')
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .append('path')
        .attr('d', 'M 0,-5 L 10,0 L 0,5')
        .attr('fill', '#999');

      const link = zoomGroup.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('class', 'link')
        .attr('marker-end', 'url(#arrowhead)');

      const node = zoomGroup.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', 'node')
        .call(drag()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended));

      node.append('circle')
        .attr('r', d => 6 - d.depth * 0.5)
        .attr('fill', d => interpolateBlues(1 - d.depth * 0.2));

      node.append('text')
        .text(d => d.label)
        .attr('x', 10)
        .attr('y', 4)
        .attr('class', 'node-label');

      // Enhanced tooltips
      const tooltip = select(container)
        .append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);

      node
        .on('mouseover', (event, d) => {
          tooltip.transition()
            .duration(200)
            .style('opacity', .9);
          tooltip.html(`
            <div class="tooltip-content">
              <strong>URL:</strong> ${d.id}<br>
              <strong>Depth:</strong> ${d.depth}
            </div>
          `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', () => {
          tooltip.transition()
            .duration(500)
            .style('opacity', 0);
        });
    }

    function ticked() {
      svgElement.selectAll('.link')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      svgElement.selectAll('.node')
        .attr('transform', d => `translate(${d.x},${d.y})`);
    }

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  }

  // Handle container resizing
  function updateDimensions() {
    if (container) {
      width = container.offsetWidth;
      height = Math.max(600, window.innerHeight * 0.6);
      if (svg) {
        select(svg)
          .attr('width', width)
          .attr('height', height);
        
        if (simulation) {
          simulation.force('center', forceCenter(width / 2, height / 2));
          simulation.alpha(0.3).restart();
        }
      }
    }
  }

  onMount(() => {
    console.log('SiteMap component mounted');
    initialize();
    window.addEventListener('resize', updateDimensions);
  });

  onDestroy(() => {
    window.removeEventListener('resize', updateDimensions);
    if (simulation) {
      simulation.stop();
    }
  });
</script>

<div class="site-map" bind:this={container}>
  <svg bind:this={svg}></svg>
</div>

<style>
  .site-map {
    margin-top: 2rem;
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    position: relative;
    width: 100%;
    height: 100%;
  }

  svg {
    display: block;
    width: 100%;
    height: 100%;
    min-height: 600px;
  }

  :global(.node-label) {
    font-size: 12px;
    pointer-events: none;
    fill: #333;
  }

  :global(.warning-text) {
    fill: #666;
    font-size: 12px;
  }

  :global(.tooltip) {
    position: absolute;
    padding: 8px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    border-radius: 4px;
    font-size: 12px;
    pointer-events: none;
    max-width: 300px;
    word-wrap: break-word;
    z-index: 100;
  }

  :global(.tooltip-content) {
    line-height: 1.4;
  }

  :global(.link) {
    stroke: #999;
    stroke-opacity: 0.6;
    stroke-width: 1;
  }
</style> 