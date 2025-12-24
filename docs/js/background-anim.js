// js/background-anim.js

(function() {
    // 确保 D3 已加载
    if (typeof d3 === 'undefined') {
        console.error("D3.js library not found!");
        return;
    }

    // 配置节点数量
    const NODE_COUNT = 80;
    
    const container = document.getElementById("d3-background");
    if (!container) return;

    const width = window.innerWidth;
    const height = window.innerHeight;

    // 生成随机数据
    const nodes = d3.range(NODE_COUNT).map(i => ({ id: i }));
    const links = [];
    
    // 随机连接一些线
    for(let i=0; i<NODE_COUNT; i++) {
        if(Math.random() > 0.8) {
            links.push({ source: i, target: Math.floor(Math.random() * NODE_COUNT) });
        }
    }

    // 创建 SVG 画布
    const svg = d3.select("#d3-background")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("display", "block"); // 防止产生滚动条空隙

    // 物理模拟器
    const simulation = d3.forceSimulation(nodes)
        .force("charge", d3.forceManyBody().strength(-100)) // 互斥力
        .force("link", d3.forceLink(links).distance(100))   // 连线力
        .force("center", d3.forceCenter(width / 2, height / 2));

    // 绘制线
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6);

    // 绘制点
    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", 5)
        .attr("fill", d => d3.schemeCategory10[d.id % 10])
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .style("cursor", "grab")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    // Tick 每一帧更新位置
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    // 拖拽处理函数
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // 窗口大小改变时调整 SVG 大小 (可选)
    window.addEventListener('resize', () => {
        svg.attr("width", window.innerWidth).attr("height", window.innerHeight);
        simulation.force("center", d3.forceCenter(window.innerWidth / 2, window.innerHeight / 2));
        simulation.alpha(0.3).restart();
    });

})();