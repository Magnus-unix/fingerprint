// js/background-anim.js

(function () {
    // 1. 基础检查
    if (typeof d3 === 'undefined') {
        console.error("D3.js library not found!");
        return;
    }

    const container = document.getElementById("d3-background");
    if (!container) return;

    // 2. 配置参数
    const NODE_COUNT = 60; // 节点稍微少一点，画面更清爽
    const NODE_RADIUS = 5; // 小球半径
    const LINK_DISTANCE = 120; // 连线长度

    let width = window.innerWidth;
    let height = window.innerHeight;

    // 3. 生成数据
    const nodes = d3.range(NODE_COUNT).map(i => ({ 
        id: i,
        // 初始位置随机分布在屏幕中心附近，防止一开始炸开太猛
        x: width / 2 + (Math.random() - 0.5) * 50,
        y: height / 2 + (Math.random() - 0.5) * 50
    }));

    const links = [];
    for (let i = 0; i < NODE_COUNT; i++) {
        // 稍微减少一点连线，让它看起来更飘逸
        if (Math.random() > 0.85) {
            links.push({ source: i, target: Math.floor(Math.random() * NODE_COUNT) });
        }
    }

    // 4. 创建 SVG
    const svg = d3.select("#d3-background")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("display", "block");

    // 5. 定义物理引擎 (核心修改部分)
    const simulation = d3.forceSimulation(nodes)
        .alphaDecay(0)         // 【永动关键】禁止自然冷却（永远不停止）
        .alphaTarget(0.02)     // 【永动关键】保持一个很低的活跃度，让它缓慢移动
        .velocityDecay(0.15)   // 摩擦力：越小动得越快，越大越像在糖浆里
        .force("charge", d3.forceManyBody().strength(-80)) // 排斥力，太大会把球推到边界贴着
        .force("link", d3.forceLink(links).distance(LINK_DISTANCE)) 
        // 使用 forceX/Y 替代 forceCenter，提供一种柔和的向心力，既不让球跑远，又不锁死在中间
        .force("x", d3.forceX(width / 2).strength(0.02)) 
        .force("y", d3.forceY(height / 2).strength(0.02))
        .force("collide", d3.forceCollide(NODE_RADIUS + 2)); // 避免球体重叠

    // 6. 绘制元素
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.4);

    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", NODE_RADIUS)
        .attr("fill", d => d3.schemeCategory10[d.id % 10])
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .style("cursor", "grab")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    // 7. 每一帧更新 (边界限制在这里)
    simulation.on("tick", () => {
        // 【边界处理】强制限制节点位置在屏幕内
        nodes.forEach(d => {
            d.x = Math.max(NODE_RADIUS, Math.min(width - NODE_RADIUS, d.x));
            d.y = Math.max(NODE_RADIUS, Math.min(height - NODE_RADIUS, d.y));
        });

        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    // --- 交互事件 ---
    function dragstarted(event, d) {
        // 拖拽时提高活跃度，反应灵敏点
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
        d3.select(this).style("cursor", "grabbing");
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        // 拖拽结束后，恢复到低活跃度的慢速漂浮状态，而不是 0
        if (!event.active) simulation.alphaTarget(0.02); 
        d.fx = null;
        d.fy = null;
        d3.select(this).style("cursor", "grab");
    }

    // 窗口调整
    window.addEventListener('resize', () => {
        width = window.innerWidth;
        height = window.innerHeight;
        svg.attr("width", width).attr("height", height);
        
        // 更新向心力的中心点
        simulation.force("x", d3.forceX(width / 2).strength(0.02));
        simulation.force("y", d3.forceY(height / 2).strength(0.02));
        
        simulation.alpha(0.3).restart();
    });

})();