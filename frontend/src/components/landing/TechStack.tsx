import { motion } from 'framer-motion';
import { Brain, Sparkles, Search, Share2 } from 'lucide-react';

const technologies = [
  {
    icon: Brain,
    name: 'Azure OpenAI',
    subtitle: 'GPT-4',
    description: 'Enterprise-grade language models',
  },
  {
    icon: Sparkles,
    name: 'Copilot Studio',
    subtitle: 'Agents',
    description: 'Intelligent workflow automation',
  },
  {
    icon: Search,
    name: 'Azure AI Search',
    subtitle: 'RAG',
    description: 'Enterprise knowledge retrieval',
  },
  {
    icon: Share2,
    name: 'Microsoft Graph',
    subtitle: 'Integration',
    description: 'Seamless M365 connectivity',
  },
];

export function TechStack() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            <span className="text-foreground">Powered by </span>
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              enterprise technology
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Built on the most trusted enterprise AI and cloud platforms
          </p>
        </motion.div>
        
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {technologies.map((tech, index) => (
            <motion.div
              key={tech.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="group text-center p-6 rounded-2xl bg-gradient-to-b from-muted/50 to-transparent border border-border hover:border-primary/50 transition-all duration-300">
                <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20 border border-primary/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <tech.icon className="w-8 h-8 text-primary" />
                </div>
                
                <h3 className="text-lg font-semibold mb-1">{tech.name}</h3>
                <div className="text-sm text-primary font-medium mb-2">{tech.subtitle}</div>
                <p className="text-sm text-muted-foreground">
                  {tech.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
