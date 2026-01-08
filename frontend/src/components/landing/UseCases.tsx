import { motion } from 'framer-motion';
import { BarChart3, Users, Megaphone, BookOpen } from 'lucide-react';

const useCases = [
  {
    icon: Megaphone,
    title: 'Marketing Campaign Reports',
    description: 'Generate comprehensive campaign performance reports with data-driven insights and recommendations.',
    image: 'marketing',
  },
  {
    icon: BarChart3,
    title: 'Sales Summaries',
    description: 'Create executive-ready sales summaries with pipeline analysis and forecasting.',
    image: 'sales',
  },
  {
    icon: Users,
    title: 'Internal Announcements',
    description: 'Draft professional internal communications for company-wide distribution.',
    image: 'announcements',
  },
  {
    icon: BookOpen,
    title: 'Knowledge Base Articles',
    description: 'Build structured knowledge base content from existing documentation and expertise.',
    image: 'knowledge',
  },
];

export function UseCases() {
  return (
    <section className="py-24 relative overflow-hidden bg-muted/20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            <span className="text-foreground">Built for </span>
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              every team
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            From marketing to sales, ContentForge adapts to your content needs
          </p>
        </motion.div>
        
        <div className="grid md:grid-cols-2 gap-6">
          {useCases.map((useCase, index) => (
            <motion.div
              key={useCase.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="group h-full p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all duration-300 flex items-start gap-5">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <useCase.icon className="w-7 h-7 text-primary" />
                </div>
                
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
                    {useCase.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {useCase.description}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
