
function renderGraficoLineasPuntaje(data, selector) {

    d3.select(selector).selectAll("*").remove();

    const puntos = data
        .filter(d => d.fecha && d.puntaje !== undefined)
        .map(d => ({
            fecha: new Date(d.fecha),
            puntaje: +d.puntaje
        }));
    console.log("Puntos procesados:", puntos);
    if (puntos.length === 0) {
        console.warn("No hay puntos para graficar.");
        return;
    }

    const width = 600, height = 300;
    const margin = { top: 20, right: 30, bottom: 50, left: 40 };

    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleTime()
        .domain(d3.extent(puntos, d => d.fecha))
        .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(puntos, d => d.puntaje)])
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

    svg.append("path")
        .datum(puntos)
        .attr("fill", "none")
        .attr("stroke", "#2ca02c")
        .attr("stroke-width", 2)
        .attr("d", line);

    svg.selectAll("circle")
        .data(puntos)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.fecha))
        .attr("cy", d => y(d.puntaje))
        .attr("r", 4)
        .attr("fill", "#2ca02c");
}
function renderGraficoLineasDistraccion(data, selector) {

    d3.select(selector).selectAll("*").remove();

    const puntos = data
        .filter(d => d.fecha && d.distraccion !== undefined)
        .map(d => ({
            fecha: new Date(d.fecha),
            distraccion: +d.distraccion
        }));
    console.log("Puntos procesados:", puntos);
    if (puntos.length === 0) {
        console.warn("No hay puntos para graficar.");
        return;
    }

    const width = 600, height = 300;
    const margin = { top: 20, right: 30, bottom: 50, left: 40 };

    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleTime()
        .domain(d3.extent(puntos, d => d.fecha))
        .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(puntos, d => d.distraccion)])
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
        .y(d => y(d.distraccion));

    svg.append("path")
        .datum(puntos)
        .attr("fill", "none")
        .attr("stroke", "#2ca02c")
        .attr("stroke-width", 2)
        .attr("d", line);

    svg.selectAll("circle")
        .data(puntos)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.fecha))
        .attr("cy", d => y(d.distraccion))
        .attr("r", 4)
        .attr("fill", "#2ca02c");
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


