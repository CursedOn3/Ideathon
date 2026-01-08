import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutTemplate, 
  Search,
  Eye,
  ArrowRight,
  FileText,
  BarChart3,
  Users,
  TrendingUp,
  DollarSign,
  Briefcase,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { mockTemplates } from '@/lib/mockData';

const categoryIcons: Record<string, React.ElementType> = {
  Marketing: BarChart3,
  Sales: TrendingUp,
  Leadership: Users,
  Research: FileText,
  Finance: DollarSign,
  Operations: Briefcase,
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function Templates() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [...new Set(mockTemplates.map((t) => t.category))];

  const filteredTemplates = mockTemplates.filter((template) => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <LayoutTemplate className="h-5 w-5 text-primary" />
            </div>
            <h1 className="font-display text-3xl font-bold text-foreground">Templates</h1>
          </div>
          <p className="text-muted-foreground">
            Choose from pre-built templates to jumpstart your report creation
          </p>
        </motion.div>

        {/* Search & Categories */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 space-y-4"
        >
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-11 border-border bg-input pl-10 text-foreground placeholder:text-muted-foreground"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant={selectedCategory === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(null)}
              className={selectedCategory === null 
                ? 'bg-primary text-primary-foreground' 
                : 'border-border text-muted-foreground hover:text-foreground'
              }
            >
              All Categories
            </Button>
            {categories.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category)}
                className={selectedCategory === category 
                  ? 'bg-primary text-primary-foreground' 
                  : 'border-border text-muted-foreground hover:text-foreground'
                }
              >
                {category}
              </Button>
            ))}
          </div>
        </motion.div>

        {/* Templates Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {filteredTemplates.map((template) => {
            const Icon = categoryIcons[template.category] || FileText;
            
            return (
              <motion.div key={template.id} variants={itemVariants}>
                <Card className="group h-full border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg">
                  <CardHeader className="pb-4">
                    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="font-display text-lg text-foreground">
                        {template.name}
                      </CardTitle>
                      <Badge variant="secondary" className="shrink-0 bg-secondary text-secondary-foreground">
                        {template.category}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
                      {template.description}
                    </p>
                    <div className="flex items-center gap-3">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="flex-1 border-border text-muted-foreground hover:text-foreground"
                          >
                            <Eye className="mr-2 h-4 w-4" />
                            Preview
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl border-border bg-card">
                          <DialogHeader>
                            <DialogTitle className="font-display text-xl text-foreground">
                              {template.name}
                            </DialogTitle>
                            <DialogDescription className="text-muted-foreground">
                              {template.description}
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 py-4">
                            <div className="rounded-lg bg-secondary/50 p-4">
                              <h4 className="mb-2 font-medium text-foreground">Template Structure</h4>
                              <ul className="space-y-2 text-sm text-muted-foreground">
                                <li className="flex items-center gap-2">
                                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                                  Executive Summary
                                </li>
                                <li className="flex items-center gap-2">
                                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                                  Key Metrics & KPIs
                                </li>
                                <li className="flex items-center gap-2">
                                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                                  Detailed Analysis
                                </li>
                                <li className="flex items-center gap-2">
                                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                                  Recommendations
                                </li>
                                <li className="flex items-center gap-2">
                                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                                  Next Steps
                                </li>
                              </ul>
                            </div>
                            <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
                              Use This Template
                              <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                      <Button 
                        size="sm"
                        className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                      >
                        Use Template
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {filteredTemplates.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-16"
          >
            <LayoutTemplate className="mb-4 h-12 w-12 text-muted-foreground/50" />
            <p className="text-lg font-medium text-muted-foreground">No templates found</p>
            <p className="text-sm text-muted-foreground/70">
              Try adjusting your search or filters
            </p>
          </motion.div>
        )}
      </div>
    </AppLayout>
  );
}
