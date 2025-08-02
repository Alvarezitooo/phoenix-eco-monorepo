export default function StorySection() {
  return (
    <section className="py-20 bg-slate-50">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">
              Né de l'expérience,
              <span className="text-orange-500"> construit pour vous</span>
            </h2>
            <div className="prose prose-lg text-slate-600 space-y-4">
              <p>
                Je m'appelle Matthieu. Après des années en tant qu'aide-soignant en EHPAD et MAS,
                j'ai vécu moi-même le défi de la reconversion vers la tech.
              </p>
              <p>
                Les lettres de motivation génériques, les CV qui ne reflétaient pas ma vraie valeur,
                les entretiens où je peinais à expliquer pourquoi mon parcours atypique était un
                atout...
              </p>
              <p className="font-semibold text-slate-900">
                Phoenix est né de cette épreuve : j'ai créé les outils que j'aurais rêvé d'avoir.
              </p>
            </div>
          </div>
          <div className="flex justify-center">
            <div className="relative">
              <div className="w-80 h-80 bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                <div className="w-72 h-72 bg-white rounded-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-32 h-32 bg-slate-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                      <span className="text-4xl">👨‍💻</span>
                    </div>
                    <h3 className="text-xl font-bold text-slate-900">Matthieu</h3>
                    <p className="text-slate-600">Créateur de Phoenix</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
