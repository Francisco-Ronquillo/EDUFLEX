
async function cargarDatosYGraficar(apiUrl) {
    const response = await fetch(apiUrl);
    const data = await response.json();

    renderGraficoBarrasAgrupadas(data, '#grafico1');
    renderGraficoLineasPuntaje(data, '#grafico2');
    renderGraficoDuracion(data, '#grafico3');
    renderGraficoDispersión(data, '#grafico4');
    renderGraficoPorFecha(data, '#grafico5');
}

function renderGraficoBarrasAgrupadas(data, selector) {
    const agrupado = {};
    data.forEach(r => {
        const nombre = r["niño__nombre_completo"];
        if (!agrupado[nombre]) agrupado[nombre] = { distracciones: 0, somnolencias: 0 };
        agrupado[nombre].distracciones += r.distracciones || 0;
        agrupado[nombre].somnolencias += r.somnolencias || 0;
    });

    const dataset = Object.entries(agrupado).map(([nombre, valores]) => ({
        nombre,
        ...valores
    }));

    const width = 600, height = 300;
    const margin = {top: 20, right: 30, bottom: 70, left: 40};

    const svg = d3.select(selector).append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleBand()
        .domain(dataset.map(d => d.nombre))
        .range([margin.left, width - margin.right])
        .padding(0.2);

    const y = d3.scaleLinear()
        .domain([0, d3.max(dataset, d => Math.max(d.distracciones, d.somnolencias))])
        .nice()
        .range([height - margin.bottom, margin.top]);

    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

    svg.selectAll(".bar1")
        .data(dataset)
        .enter()
        .append("rect")
        .attr("x", d => x(d.nombre))
        .attr("y", d => y(d.distracciones))
        .attr("width", x.bandwidth() / 2)
        .attr("height", d => y(0) - y(d.distracciones))
        .attr("fill", "#1f77b4");

    svg.selectAll(".bar2")
        .data(dataset)
        .enter()
        .append("rect")
        .attr("x", d => x(d.nombre) + x.bandwidth() / 2)
        .attr("y", d => y(d.somnolencias))
        .attr("width", x.bandwidth() / 2)
        .attr("height", d => y(0) - y(d.somnolencias))
        .attr("fill", "#ff7f0e");
}

function renderGraficoLineasPuntaje(data, selector) {
    const agrupado = {};
    data.forEach(d => {
        const nombre = d["niño__nombre_completo"];
        if (!agrupado[nombre]) agrupado[nombre] = [];
        agrupado[nombre].push({fecha: new Date(d.fecha), puntaje: +d.puntaje});
    });

    const width = 600, height = 300;
    const margin = {top: 20, right: 30, bottom: 50, left: 40};

    const svg = d3.select(selector).append("svg")
        .attr("width", width)
        .attr("height", height);

    const allData = Object.values(agrupado).flat();
    const x = d3.scaleTime()
        .domain(d3.extent(allData, d => d.fecha))
        .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(allData, d => d.puntaje)])
        .nice()
        .range([height - margin.bottom, margin.top]);

    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y-%m-%d")))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

    const line = d3.line()
        .x(d => x(d.fecha))
        .y(d => y(d.puntaje));

    Object.entries(agrupado).forEach(([nombre, puntos]) => {
        svg.append("path")
            .datum(puntos)
            .attr("fill", "none")
            .attr("stroke", d3.schemeCategory10[Math.floor(Math.random() * 10)])
            .attr("stroke-width", 2)
            .attr("d", line);
    });
}

function renderGraficoDuracion(data, selector) {
    const agrupado = {};
    data.forEach(r => {
        const nombre = r["niño__nombre_completo"];
        const dur = r.duracion_evaluacion ? parseFloat(r.duracion_evaluacion.replace(":", ".")) : 0;
        if (!agrupado[nombre]) agrupado[nombre] = [];
        agrupado[nombre].push(dur);
    });

    const promedios = Object.entries(agrupado).map(([nombre, valores]) => ({
        nombre,
        promedio: valores.reduce((a, b) => a + b, 0) / valores.length
    }));

    const width = 600, height = 300;
    const margin = {top: 20, right: 30, bottom: 70, left: 50};

    const svg = d3.select(selector).append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleBand()
        .domain(promedios.map(d => d.nombre))
        .range([margin.left, width - margin.right])
        .padding(0.3);

    const y = d3.scaleLinear()
        .domain([0, d3.max(promedios, d => d.promedio)])
        .nice()
        .range([height - margin.bottom, margin.top]);

    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

    svg.selectAll("rect")
        .data(promedios)
        .enter()
        .append("rect")
        .attr("x", d => x(d.nombre))
        .attr("y", d => y(d.promedio))
        .attr("width", x.bandwidth())
        .attr("height", d => y(0) - y(d.promedio))
        .attr("fill", "#6a3d9a");
}

function renderGraficoDispersión(data, selector) {
    const dataset = data.map(d => ({
        puntaje: +d.puntaje || 0,
        distracciones: +d.distracciones || 0
    }));

    const width = 600, height = 300;
    const margin = {top: 20, right: 20, bottom: 50, left: 50};

    const svg = d3.select(selector).append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleLinear()
        .domain([0, d3.max(dataset, d => d.distracciones)])
        .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(dataset, d => d.puntaje)])
        .range([height - margin.bottom, margin.top]);

    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

    svg.selectAll("circle")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.distracciones))
        .attr("cy", d => y(d.puntaje))
        .attr("r", 5)
        .attr("fill", "#e41a1c");
}

function renderGraficoPorFecha(data, selector) {
    const conteo = {};
    data.forEach(d => {
        const fecha = d.fecha;
        conteo[fecha] = (conteo[fecha] || 0) + 1;
    });

    const dataset = Object.entries(conteo).map(([fecha, cantidad]) => ({
        fecha: new Date(fecha),
        cantidad
    }));

    const width = 600, height = 300;
    const margin = {top: 20, right: 20, bottom: 50, left: 50};

    const svg = d3.select(selector).append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleTime()
        .domain(d3.extent(dataset, d => d.fecha))
        .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(dataset, d => d.cantidad)])
        .range([height - margin.bottom, margin.top]);

    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y-%m-%d")))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

    svg.append("path")
        .datum(dataset)
        .attr("fill", "none")
        .attr("stroke", "#4daf4a")
        .attr("stroke-width", 2)
        .attr("d", d3.line()
            .x(d => x(d.fecha))
            .y(d => y(d.cantidad))
        );
}

function renderGraficoPastelReporte(data, selector) {
    const valores = [
        { etiqueta: "Somnolencias", valor: data.somnolencias },
        { etiqueta: "Distracciones", valor: data.distracciones }
    ];

    const width = 300, height = 300, radius = Math.min(width, height) / 2;

    const color = d3.scaleOrdinal()
        .domain(valores.map(d => d.etiqueta))
        .range(["#e41a1c", "#377eb8"]);

    const pie = d3.pie()
        .value(d => d.valor);

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius - 10);

    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const arcs = svg.selectAll("arc")
        .data(pie(valores))
        .enter()
        .append("g");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.etiqueta));

    arcs.append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .attr("text-anchor", "middle")
        .text(d => `${d.data.etiqueta}: ${d.data.valor}`);
}

function renderGraficoLineaSomnolencia(data, contenedor) {
    // Limpia cualquier gráfico anterior
    d3.select(contenedor).selectAll("*").remove();

    // Tamaño y márgenes
    const margin = { top: 30, right: 30, bottom: 50, left: 60 };
    const width = 600 - margin.left - margin.right;
    const height = 350 - margin.top - margin.bottom;

    // Crear SVG
    const svg = d3.select(contenedor)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Función para convertir índice a ordinal (1ra, 2da, 3ra, 4ta, ...)
    function ordinalEtiqueta(i) {
        if (i === 0) return "1ra";
        if (i === 1) return "2da";
        if (i === 2) return "3ra";
        return `${i + 1}ta`;
    }

    const etiquetasX = data.map((_, i) => ordinalEtiqueta(i));

    // Escalas
    const x = d3.scalePoint()
        .domain(etiquetasX)
        .range([0, width])
        .padding(0.5);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data)])
        .range([height, 0]);

    // Eje X
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    // Eje Y
    svg.append("g")
        .call(d3.axisLeft(y));

    // Línea
    const linea = d3.line()
        .x((d, i) => x(etiquetasX[i]))
        .y(d => y(d))
        .curve(d3.curveMonotoneX);

    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#e67e22")
        .attr("stroke-width", 3)
        .attr("d", linea);

    // Círculos en los puntos
    svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", (d, i) => x(etiquetasX[i]))
        .attr("cy", d => y(d))
        .attr("r", 5)
        .attr("fill", "#e67e22");

    // Título
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .text("Duración de Somnolencias (segundos)");
}

function renderGraficoLineaDistraccion(data, selector) {
    const datos = data.tiempos_distraccion || [];
    const svgWidth = 500, svgHeight = 250, margin = {top: 20, right: 20, bottom: 30, left: 40};
    const width = svgWidth - margin.left - margin.right;
    const height = svgHeight - margin.top - margin.bottom;

    d3.select(selector).selectAll("*").remove();

    const svg = d3.select(selector)
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear()
        .domain([1, datos.length])
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(datos) || 1])
        .range([height, 0]);

    const line = d3.line()
        .x((d, i) => x(i + 1))
        .y(d => y(d))
        .curve(d3.curveMonotoneX); // curva suave

    // Línea azul
    svg.append("path")
        .datum(datos)
        .attr("fill", "none")
        .attr("stroke", "#3498db")
        .attr("stroke-width", 2)
        .attr("d", line);

    // Puntos
    svg.selectAll(".punto")
        .data(datos)
        .enter()
        .append("circle")
        .attr("class", "punto")
        .attr("cx", (d, i) => x(i + 1))
        .attr("cy", d => y(d))
        .attr("r", 4)
        .attr("fill", "#3498db");

    // Ejes
    svg.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x)
        .ticks(datos.length)
        .tickFormat((d, i) => `${d}ª`));

    svg.append("g")
        .call(d3.axisLeft(y));

    // Título
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", -5)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .text("Duración de Distracciones (segundos)");
}

function renderGraficoPastelTiempo(data, selector) {
    const valores = [
        { etiqueta: "Tiempo de Distracción", valor: data.total_tiempo_distraccion },
        { etiqueta: "Tiempo de Somnolencia", valor: data.total_somnolencia },
        { etiqueta: "Tiempo de Evaluación", valor: data.total_tiempo_evaluacion }
    ];

    const width = 300, height = 300, radius = Math.min(width, height) / 2;

    const color = d3.scaleOrdinal()
        .domain(valores.map(d => d.etiqueta))
        .range(["#e41a1c", "#377eb8", "#4daf4a"]);

    const pie = d3.pie()
        .value(d => d.valor);

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius - 10);

    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const arcs = svg.selectAll("arc")
        .data(pie(valores))
        .enter()
        .append("g");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.etiqueta));

    arcs.append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .text(d => `${d.data.etiqueta}: ${d.data.valor}`);
}


