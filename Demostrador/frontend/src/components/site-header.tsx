"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Crosshair, Home } from "lucide-react";
import { Brand } from "./brand";

const links = [
  { href: "/", label: "Inicio", icon: Home },
  { href: "/demo", label: "Demostrador", icon: Crosshair },
  { href: "/monitoreo", label: "Monitoreo", icon: BarChart3 },
];
export function SiteHeader() {
  const pathname = usePathname();
  return <header className="site-header"><div className="shell header-inner">
    <Link href="/" className="brand-link"><Brand/></Link>
    <nav aria-label="Navegación principal">{links.map(({href,label,icon:Icon}) => {
      const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
      return <Link key={href} href={href} className={active ? "nav-link active" : "nav-link"}><Icon size={18}/><span>{label}</span></Link>;
    })}</nav>
  </div></header>;
}
