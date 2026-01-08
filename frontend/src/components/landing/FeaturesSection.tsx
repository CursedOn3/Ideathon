import { motion } from 'framer-motion';
import { Bot, Database, Send, ShieldCheck } from 'lucide-react';

const features = [
  {
    icon: Bot,
    title: 'Agentic AI Workflows',
    description: 'Planning and generator agents collaborate to produce accurate, structured content.',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Database,
    title: 'Enterprise-Grade RAG',
    description: 'Grounded responses using internal SharePoint documents via Azure AI Search.',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: Send,
    title: 'One-Click Publishing',
    description: 'Automatically publish reports to SharePoint and Teams.',
    gradient: 'from-orange-500 to-amber-500',
  },
  {
    icon: ShieldCheck,
    title: 'Responsible AI',
    description: 'Citation tracking, originality checks, and compliance-ready outputs.',
    gradient: 'from-green-500 to-emerald-500',
  },
];

export function FeaturesSection() {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background" />
      
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            <span className="text-foreground">Everything you need for</span>
            <br />
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              enterprise content
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Powerful AI capabilities designed for the enterprise, with security and compliance built in.
          </p>
        </motion.div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="group h-full p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} p-0.5 mb-5`}>
                  <div className="w-full h-full rounded-xl bg-card flex items-center justify-center group-hover:bg-transparent transition-colors">
                    <feature.icon className={`w-7 h-7 text-foreground group-hover:text-white transition-colors`} />
                  </div>
                </div>
                
                <h3 className="text-xl font-semibold mb-3 group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
