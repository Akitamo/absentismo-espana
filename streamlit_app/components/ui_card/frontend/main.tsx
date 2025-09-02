import "./style.css"
import Plotly from "plotly.js-dist-min"
import { Streamlit } from "streamlit-component-lib"

type Props = {
  type: "metric" | "plotly" | "html"
  title: string
  subtitle?: string
  icon?: string
  value?: string
  height?: number
  fig?: any
  modebar?: boolean
  html?: string
  tokens?: Record<string, any>
}

const root = document.getElementById("root") as HTMLDivElement

function applyTokens(tokens: Record<string, any> = {}) {
  const cssVars: Record<string, string> = {
    "--surface": tokens.color_surface ?? "var(--surface)",
    "--border": tokens.color_border ?? "var(--border)",
    "--radius": tokens.radius ?? "14px",
    "--primary": tokens.color_primary ?? "var(--primary)",
  }
  Object.entries(cssVars).forEach(([k, v]) => {
    document.documentElement.style.setProperty(k, v)
  })
}

function renderMetric(p: Props, body: HTMLElement) {
  const v = document.createElement("div")
  v.className = "value"
  v.textContent = p.value ?? ""
  body.appendChild(v)
}

function renderHTML(p: Props, body: HTMLElement) {
  const slot = document.createElement("div")
  slot.innerHTML = p.html ?? ""
  body.appendChild(slot)
}

function renderPlotly(p: Props, body: HTMLElement) {
  const plot = document.createElement("div")
  plot.style.width = "100%"
  plot.style.height = ((p.height ?? 360) - 64) + "px"   // un poco más de aire bajo la cabecera
  body.appendChild(plot)

  // Tema Plotly alineado con el card
  const layout = {
    ...(p.fig.layout || {}),
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 8, r: 8, t: 6, b: 24 },
    xaxis: {
      ...(p.fig.layout?.xaxis || {}),
      gridcolor: "#EEF1F5",
      zeroline: false,
      linecolor: "#E7EBF0",
      tickfont: { color: "#6B7280", size: 11 }
    },
    yaxis: {
      ...(p.fig.layout?.yaxis || {}),
      gridcolor: "#EEF1F5",
      zeroline: false,
      linecolor: "#E7EBF0",
      tickfont: { color: "#6B7280", size: 11 }
    },
    font: { family: "Inter, system-ui, -apple-system, Segoe UI, Roboto", color: "#0F172A" }
  }

  // color primario por defecto si no lo trae el fig
  if (!p.fig.data?.length) return
  const data = p.fig.data.map((trace: any) => {
    if (trace.type === "scatter" && !trace.line?.color){
      return {
        ...trace,
        line: { ...(trace.line || {}), color: "#1B59F8", width: 2 },
        fill: trace.fill ?? "tozeroy",
        fillcolor: "rgba(27,89,248,0.08)"
      }
    }
    return trace
  })

  Plotly.react(plot, data, layout, {
    displayModeBar: !!p.modebar,
    responsive: true
  })
}

function render(props: Props) {
  root.innerHTML = ""
  applyTokens(props.tokens)

  const card = document.createElement("div")
  card.className = "card"
  card.style.height = (props.height ?? 300) + "px"

  // header
  const header = document.createElement("div")
  header.className = "header"
  if (props.icon) {
    const pill = document.createElement("div")
    pill.className = "pill"
    pill.textContent = props.icon
    header.appendChild(pill)
  }
  const titleBox = document.createElement("div")
  const title = document.createElement("div")
  title.className = "title"
  title.textContent = props.title ?? ""
  titleBox.appendChild(title)
  if (props.subtitle) {
    const sub = document.createElement("div")
    sub.className = "subtitle"
    sub.textContent = props.subtitle
    titleBox.appendChild(sub)
  }
  header.appendChild(titleBox)
  card.appendChild(header)

  // body
  const body = document.createElement("div")
  body.className = "body"

  if (props.type === "metric") renderMetric(props, body)
  if (props.type === "html") renderHTML(props, body)
  if (props.type === "plotly" && props.fig) renderPlotly(props, body)

  card.appendChild(body)
  root.appendChild(card)

  Streamlit.setFrameHeight(props.height ?? 300)
}

/** Conexión con Streamlit (vanilla) */
function onRender(event: any) {
  const props = event.detail.args as Props
  render(props)
}
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
Streamlit.setComponentReady()