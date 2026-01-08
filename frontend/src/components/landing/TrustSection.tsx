import { motion } from 'framer-motion';

const logos = [
  'Enterprise Co',
  'TechCorp',
  'GlobalFin',
  'DataSync',
  'CloudFirst',
  'InnovateLabs',
];

export function TrustSection() {
  return (
    <section className="py-16 border-y border-border/50">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-10"
        >
          <p className="text-muted-foreground text-sm uppercase tracking-wider mb-2">
            Trusted by enterprise teams worldwide
          </p>
          <p className="text-xs text-muted-foreground/70">
            Built on Microsoft Azure, Copilot Studio, and OpenAI technology
          </p>
        </motion.div>
        
        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12">
          {logos.map((logo, index) => (
            <motion.div
              key={logo}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex items-center justify-center"
            >
              <div className="px-6 py-3 rounded-lg bg-muted/30 border border-border/50 hover:border-primary/30 transition-colors">
                <span className="text-lg font-semibold text-muted-foreground/70 hover:text-foreground transition-colors">
                  {logo}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
