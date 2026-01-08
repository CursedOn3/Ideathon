import { motion } from 'framer-motion';
import { MessageSquare, Cpu, Rocket } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: MessageSquare,
    title: 'Prompt',
    description: 'Describe what content you need in plain English.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    number: '02',
    icon: Cpu,
    title: 'Generate',
    description: 'AI agents research, draft, and refine content using enterprise data.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    number: '03',
    icon: Rocket,
    title: 'Publish',
    description: 'Content is automatically delivered to SharePoint and Teams.',
    color: 'from-orange-500 to-amber-500',
  },
];

export function HowItWorks() {
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
            <span className="text-foreground">How it </span>
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              works
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to transform your content creation workflow
          </p>
        </motion.div>
        
        <div className="relative">
          {/* Connection line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-border to-transparent transform -translate-y-1/2" />
          
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
            {steps.map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                className="relative"
              >
                <div className="text-center">
                  {/* Step number background */}
                  <div className="relative inline-block mb-6">
                    <div className={`w-24 h-24 rounded-2xl bg-gradient-to-br ${step.color} p-0.5`}>
                      <div className="w-full h-full rounded-2xl bg-card flex items-center justify-center">
                        <step.icon className="w-10 h-10 text-foreground" />
                      </div>
                    </div>
                    <div className={`absolute -top-3 -right-3 w-8 h-8 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center`}>
                      <span className="text-xs font-bold text-white">{step.number}</span>
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-3">{step.title}</h3>
                  <p className="text-muted-foreground max-w-xs mx-auto">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
