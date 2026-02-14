import "./globals.css";

export const metadata = {
  title: "TrustStack AI Assurance Hub",
  description: "TrustStack AI GRC Workbench — config-driven packs → controls → evidence → audit-ready."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div style={{background:"#0b1220", color:"white"}}>
          <div className="container" style={{paddingTop:18, paddingBottom:18}}>
            <div className="hstack" style={{justifyContent:"space-between"}}>
              <div>
                <div style={{fontWeight:800, fontSize:18}}>TrustStack AI Assurance Hub</div>
                <div className="small" style={{color:"#cbd5e1"}}>AI GRC Workbench · Config-driven packs → controls → evidence → audit-ready.</div>
              </div>
              <div className="hstack">
                <a className="btn" href="/" style={{background:"transparent", color:"white", borderColor:"#334155"}}>Home</a>
                <a className="btn" href="/new" style={{background:"white", color:"#0b1220"}}>New Project</a>
              </div>
            </div>
          </div>
        </div>
        {children}
        <div className="container small" style={{paddingBottom:32}}>
          <hr />
          <div>© {new Date().getFullYear()} TrustStack AI GRC (scaffold). Not legal advice.</div>
        </div>
      </body>
    </html>
  );
}
