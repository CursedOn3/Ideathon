import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FilePlus, 
  FileText, 
  TrendingUp, 
  Clock,
  ArrowRight,
  Sparkles,
  Zap,
  BarChart3,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/contexts/AuthContext';
import { mockReports } from '@/lib/mockData';

const stats = [
  { label: 'Reports Created', value: '127', icon: FileText, trend: '+12%' },
  { label: 'Time Saved', value: '45hrs', icon: Clock, trend: '+8%' },
  { label: 'Accuracy Rate', value: '98.5%', icon: TrendingUp, trend: '+2%' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function Dashboard() {
  const { user } = useAuth();
  const recentReports = mockReports.slice(0, 3);

  return (
    <AppLayout>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-8"
      >
        {/* Welcome Banner */}
        <motion.div variants={itemVariants} className="gradient-border overflow-hidden">
          <div className="relative overflow-hidden rounded-lg bg-card p-8">
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-[60px]" />
            <div className="absolute -bottom-10 -left-10 h-40 w-40 rounded-full bg-accent/10 blur-[40px]" />
            
            <div className="relative z-10 flex items-center justify-between">
              <div className="max-w-xl">
                <div className="mb-2 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-accent" />
                  <span className="text-sm font-medium text-accent">AI-Powered</span>
                </div>
                <h1 className="font-display text-3xl font-bold text-foreground">
                  Welcome back, {user?.name?.split(' ')[0] || 'User'}
                </h1>
                <p className="mt-2 text-lg text-muted-foreground">
                  Generate enterprise reports <span className="gradient-text font-semibold">10× faster</span> with intelligent automation and real-time insights.
                </p>
                <div className="mt-6 flex gap-4">
                  <Button asChild className="bg-primary text-primary-foreground hover:bg-primary/90">
                    <Link to="/create">
                      <FilePlus className="mr-2 h-4 w-4" />
                      Create New Report
                    </Link>
                  </Button>
                  <Button variant="outline" asChild className="border-border text-foreground hover:bg-secondary">
                    <Link to="/templates">
                      Browse Templates
                    </Link>
                  </Button>
                </div>
              </div>
              <div className="hidden lg:block">
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                  className="flex h-32 w-32 items-center justify-center rounded-2xl bg-primary/10"
                >
                  <Zap className="h-16 w-16 text-primary" />
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div variants={itemVariants} className="grid gap-6 md:grid-cols-3">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label} className="glass-hover border-border bg-card">
                <CardContent className="flex items-center gap-4 p-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <div className="flex items-baseline gap-2">
                      <span className="font-display text-2xl font-bold text-foreground">{stat.value}</span>
                      <span className="text-sm font-medium text-success">{stat.trend}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </motion.div>

        {/* Recent Reports & Quick Actions */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Recent Reports */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <Card className="border-border bg-card">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="font-display text-lg text-foreground">Recent Reports</CardTitle>
                <Button variant="ghost" size="sm" asChild className="text-muted-foreground hover:text-foreground">
                  <Link to="/reports">
                    View All
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentReports.map((report) => (
                    <Link
                      key={report.id}
                      to={`/reports/${report.id}`}
                      className="group flex items-center justify-between rounded-lg border border-border p-4 transition-colors hover:border-primary/30 hover:bg-secondary/50"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                          <FileText className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div>
                          <p className="font-medium text-foreground group-hover:text-primary transition-colors">
                            {report.title}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(report.createdAt).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </p>
                        </div>
                      </div>
                      <StatusBadge variant={report.status}>
                        {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                      </StatusBadge>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Quick Actions */}
          <motion.div variants={itemVariants}>
            <Card className="border-border bg-card">
              <CardHeader>
                <CardTitle className="font-display text-lg text-foreground">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link
                  to="/create"
                  className="group flex items-center gap-3 rounded-lg border border-border p-4 transition-all hover:border-primary/30 hover:bg-secondary/50"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <FilePlus className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">New Report</p>
                    <p className="text-sm text-muted-foreground">Start from scratch</p>
                  </div>
                </Link>

                <Link
                  to="/templates"
                  className="group flex items-center gap-3 rounded-lg border border-border p-4 transition-all hover:border-primary/30 hover:bg-secondary/50"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10">
                    <BarChart3 className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Use Template</p>
                    <p className="text-sm text-muted-foreground">Pre-built formats</p>
                  </div>
                </Link>

                <Link
                  to="/reports"
                  className="group flex items-center gap-3 rounded-lg border border-border p-4 transition-all hover:border-primary/30 hover:bg-secondary/50"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-info/10">
                    <FileText className="h-5 w-5 text-info" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Browse Reports</p>
                    <p className="text-sm text-muted-foreground">View all reports</p>
                  </div>
                </Link>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </motion.div>
    </AppLayout>
  );
}
