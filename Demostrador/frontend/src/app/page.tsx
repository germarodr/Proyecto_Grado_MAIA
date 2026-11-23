import Link from "next/link";
import { BarChart3, Boxes, Cloud, Cpu, Database, FileSearch, ScanSearch } from "lucide-react";
import { Brand } from "@/components/brand";
import { Panel } from "@/components/ui";
import functions from "../../data/functions.json";

const models = [
  {icon:Cpu,title:"Encoder fine-tuned",text:"SciBERT ajustado con el contexto de la cita y los tres fragmentos más similares del artículo citado, con su sección."},
  {icon:Boxes,title:"Modelo open-weight",text:"Modelo de pesos abiertos (1–8B) de Hugging Face, servido con Ollama dentro del despliegue, con el mismo prompt y la misma entrada del modelo comercial."},
  {icon:Cloud,title:"Modelo comercial",text:"Gemini 3.5 Flash-Lite vía API con el prompt v11.1 de A5: contexto de la cita, título y resumen del citado, con la política de recorte de SciBERT base."},
];

export default function HomePage() {
  return <div className="shell"><section className="hero"><div className="hero-copy"><h1>CiteScope</h1><h2>Función retórica de las citas académicas</h2><p>Para cada cita, mostramos los tres fragmentos del artículo citado más cercanos a su contexto y clasificamos para qué se usa la cita: antecedentes, comparación, aplicación de un método, evidencia, entre otras.</p><div className="hero-actions"><Link className="btn primary" href="/demo"><FileSearch size={20}/>Abrir el demostrador</Link><Link className="btn" href="/monitoreo"><ScanSearch size={20}/>Ver monitoreo</Link></div><div className="trust"><Database size={17}/>40 ejemplos validados por humanos · 9 funciones de cita · arXiv Computer Science</div></div><div className="hero-visual"><Brand/></div></section>
  <section className="benefit-grid">{models.map(({icon:Icon,title,text})=><Panel className="benefit" key={title}><span className="icon-bubble"><Icon size={25}/></span><div><h3>{title}</h3><p>{text}</p></div></Panel>)}</section>
  <h2 className="section-title"><BarChart3 size={22}/>Las 9 funciones de cita</h2>
  <section className="function-grid">{functions.map(f=><Panel className="function-card" key={f.code}><span className="function-dot" style={{background:f.color}}/><div><h3>{f.nameEs}</h3><small>{f.code}</small><p>{f.description}</p></div></Panel>)}</section></div>;
}
