import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Edit3, 
  Download, 
  Share2, 
  ExternalLink,
  BookOpen,
  Table,
  Lightbulb,
  Link as LinkIcon,
  Check,
  Loader2,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { mockGeneratedReport } from '@/lib/mockData';

export default function ReportPreview() {
  const location = useLocation();
  const prompt = location.state?.prompt || 'Q4 2024 Enterprise Performance Analysis';
  const [isPublishing, setIsPublishing] = useState(false);
  const [isPublished, setIsPublished] = useState(false);

  const report = mockGeneratedReport;

  const handlePublish = async () => {
    setIsPublishing(true);
    // Simulate publishing to SharePoint/Teams
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsPublishing(false);
    setIsPublished(true);
  };

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-wrap items-center justify-between gap-4"
        >
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" asChild className="text-muted-foreground hover:text-foreground">
              <Link to="/create">
                <ArrowLeft className="h-5 w-5" />
              </Link>
            </Button>
            <div>
              <h1 className="font-display text-2xl font-bold text-foreground">
                Q4 2024 Enterprise Performance Analysis
              </h1>
              <p className="text-sm text-muted-foreground">
                Generated from: "{prompt.slice(0, 50)}..."
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="border-border text-foreground hover:bg-secondary">
              <Edit3 className="mr-2 h-4 w-4" />
              Edit
            </Button>
            <Button variant="outline" size="sm" className="border-border text-foreground hover:bg-secondary">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button
              size="sm"
              onClick={handlePublish}
              disabled={isPublishing || isPublished}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {isPublishing ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : isPublished ? (
                <Check className="mr-2 h-4 w-4" />
              ) : (
                <Share2 className="mr-2 h-4 w-4" />
              )}
              {isPublished ? 'Published' : 'Publish to SharePoint'}
            </Button>
          </div>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-6 lg:col-span-2"
          >
            {/* Executive Summary */}
            <Card className="border-border bg-card">
              <CardHeader className="flex flex-row items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <BookOpen className="h-5 w-5 text-primary" />
                </div>
                <CardTitle className="font-display text-foreground">Executive Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="leading-relaxed text-muted-foreground">
                  {report.executiveSummary}
                </p>
              </CardContent>
            </Card>

            {/* Sections */}
            {report.sections.map((section, index) => (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                <Card className="border-border bg-card">
                  <CardHeader className="flex flex-row items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                      {section.type === 'table' ? (
                        <Table className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <Lightbulb className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                    <CardTitle className="font-display text-foreground">{section.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {section.type === 'table' && section.data ? (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-border">
                              {Object.keys(section.data[0]).map((key) => (
                                <th
                                  key={key}
                                  className="pb-3 text-left text-sm font-medium uppercase tracking-wider text-muted-foreground"
                                >
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {section.data.map((row, rowIndex) => (
                              <tr key={rowIndex} className="border-b border-border/50 last:border-0">
                                {Object.entries(row).map(([key, value], cellIndex) => (
                                  <td
                                    key={key}
                                    className={`py-3 text-sm ${
                                      cellIndex === 0 ? 'font-medium text-foreground' : 'text-muted-foreground'
                                    } ${
                                      String(value).startsWith('+') ? 'text-success' : 
                                      String(value).startsWith('-') ? 'text-destructive' : ''
                                    }`}
                                  >
                                    {String(value)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="leading-relaxed text-muted-foreground">
                        {section.content}
                      </p>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* Citations Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="sticky top-8 border-border bg-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-display text-foreground">
                  <LinkIcon className="h-5 w-5" />
                  Sources & Citations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {report.citations.map((citation, index) => (
                  <div key={citation.id}>
                    <div className="rounded-lg bg-secondary/50 p-4">
                      <div className="mb-2 flex items-start justify-between gap-2">
                        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20 text-xs font-medium text-primary">
                          {index + 1}
                        </span>
                        {citation.url && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-muted-foreground hover:text-foreground"
                            asChild
                          >
                            <a href={citation.url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          </Button>
                        )}
                      </div>
                      <p className="mb-1 text-sm font-medium text-foreground">{citation.source}</p>
                      <p className="text-xs text-muted-foreground">{citation.excerpt}</p>
                    </div>
                    {index < report.citations.length - 1 && <Separator className="my-4" />}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </AppLayout>
  );
}
