import Link from "next/link";
import { Landmark } from "lucide-react";
export function SiteFooter() {
  return <footer className="site-footer"><div className="shell footer-inner">
    <Landmark size={30}/><div className="footer-copy"><strong>Proyecto de grado · Maestría en Inteligencia Artificial</strong><span>Grupo de investigación FLAG – TICsW · Departamento de Ingeniería de Sistemas y Computación</span><span>Universidad de los Andes</span></div>
    <div className="footer-links"><Link href="/">Acerca del proyecto</Link><Link href="/demo">Demostrador</Link><Link href="/monitoreo">Monitoreo</Link></div>
  </div></footer>;
}
