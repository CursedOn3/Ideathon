import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Search, 
  Filter, 
  MoreHorizontal,
  Eye,
  Edit3,
  Trash2,
  Download,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/ui/status-badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { mockReports } from '@/lib/mockData';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
};

export default function MyReports() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'draft' | 'published'>('all');

  const filteredReports = mockReports.filter((report) => {
    const matchesSearch = report.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || report.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <AppLayout>
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="font-display text-3xl font-bold text-foreground">My Reports</h1>
          <p className="mt-2 text-muted-foreground">
            View and manage all your generated reports
          </p>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6 flex flex-wrap items-center gap-4"
        >
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search reports..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-10 border-border bg-input pl-10 text-foreground placeholder:text-muted-foreground"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={statusFilter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter('all')}
              className={statusFilter === 'all' 
                ? 'bg-primary text-primary-foreground' 
                : 'border-border text-muted-foreground hover:text-foreground'
              }
            >
              All
            </Button>
            <Button
              variant={statusFilter === 'published' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter('published')}
              className={statusFilter === 'published' 
                ? 'bg-primary text-primary-foreground' 
                : 'border-border text-muted-foreground hover:text-foreground'
              }
            >
              Published
            </Button>
            <Button
              variant={statusFilter === 'draft' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter('draft')}
              className={statusFilter === 'draft' 
                ? 'bg-primary text-primary-foreground' 
                : 'border-border text-muted-foreground hover:text-foreground'
              }
            >
              Drafts
            </Button>
          </div>
        </motion.div>

        {/* Reports List */}
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between border-b border-border">
            <CardTitle className="font-display text-lg text-foreground">
              {filteredReports.length} Reports
            </CardTitle>
            <Button variant="outline" size="sm" className="border-border text-muted-foreground hover:text-foreground">
              <Filter className="mr-2 h-4 w-4" />
              More Filters
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
            >
              {filteredReports.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16">
                  <FileText className="mb-4 h-12 w-12 text-muted-foreground/50" />
                  <p className="text-lg font-medium text-muted-foreground">No reports found</p>
                  <p className="text-sm text-muted-foreground/70">
                    Try adjusting your search or filters
                  </p>
                </div>
              ) : (
                filteredReports.map((report, index) => (
                  <motion.div
                    key={report.id}
                    variants={itemVariants}
                    className={`flex items-center justify-between p-4 transition-colors hover:bg-secondary/30 ${
                      index !== filteredReports.length - 1 ? 'border-b border-border' : ''
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                      </div>
                      <div>
                        <Link
                          to={`/reports/${report.id}`}
                          className="font-medium text-foreground hover:text-primary transition-colors"
                        >
                          {report.title}
                        </Link>
                        <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
                          <span>
                            Created {new Date(report.createdAt).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </span>
                          {report.template && (
                            <>
                              <span>•</span>
                              <span>{report.template}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <StatusBadge variant={report.status}>
                        {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                      </StatusBadge>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-48 border-border bg-popover">
                          <DropdownMenuItem asChild className="text-popover-foreground focus:bg-secondary">
                            <Link to={`/reports/${report.id}`}>
                              <Eye className="mr-2 h-4 w-4" />
                              View Report
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-popover-foreground focus:bg-secondary">
                            <Edit3 className="mr-2 h-4 w-4" />
                            Edit Report
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-popover-foreground focus:bg-secondary">
                            <Download className="mr-2 h-4 w-4" />
                            Export PDF
                          </DropdownMenuItem>
                          <DropdownMenuSeparator className="bg-border" />
                          <DropdownMenuItem className="text-destructive focus:bg-destructive/10 focus:text-destructive">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete Report
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </motion.div>
                ))
              )}
            </motion.div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
