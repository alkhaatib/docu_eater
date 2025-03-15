import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  LinearProgress,
  ListItemIcon,
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';

// Mock data - in a real app, this would come from an API
const getMockTaskDetail = (id: string) => ({
  id,
  url: 'https://docs.python.org',
  startTime: '2023-03-10T08:30:00',
  endTime: '2023-03-10T09:45:00',
  status: 'completed',
  pagesIndexed: 243,
  maxPages: 300,
  errorCount: 2,
  crawlDepth: 4,
  crawlType: 'breadth',
  documentMap: {
    id: 'root',
    name: 'Python Documentation',
    children: [
      {
        id: '1',
        name: 'Getting Started',
        children: [
          { id: '1.1', name: 'Installation', children: [] },
          { id: '1.2', name: 'First Steps', children: [] },
        ],
      },
      {
        id: '2',
        name: 'Language Reference',
        children: [
          { id: '2.1', name: 'Lexical Analysis', children: [] },
          { id: '2.2', name: 'Data Model', children: [] },
        ],
      },
    ],
  },
  recentPages: [
    { url: 'https://docs.python.org/tutorial/index.html', title: 'Tutorial' },
    { url: 'https://docs.python.org/reference/index.html', title: 'Language Reference' },
    { url: 'https://docs.python.org/library/index.html', title: 'Library Reference' },
  ],
});

const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulating API call
    setTimeout(() => {
      setTask(getMockTaskDetail(taskId || '0'));
      setLoading(false);
    }, 500);
  }, [taskId]);

  const renderDocumentTree = (node: any, level = 0) => {
    const isFolder = node.children && node.children.length > 0;
    
    return (
      <React.Fragment key={node.id}>
        <ListItem sx={{ pl: level * 2 }}>
          <ListItemIcon>
            {isFolder ? <FolderIcon color="primary" /> : <DescriptionIcon color="info" />}
          </ListItemIcon>
          <ListItemText primary={node.name} />
        </ListItem>
        {isFolder && node.children.map((child: any) => renderDocumentTree(child, level + 1))}
      </React.Fragment>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <LinearProgress />
          <Typography variant="h5" sx={{ mt: 2 }}>
            Loading task details...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (!task) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h5" color="error">
            Task not found
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Task Detail: {task.id}
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Crawl Information
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="URL" secondary={task.url} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Status"
                      secondary={
                        <Chip
                          label={task.status}
                          color={task.status === 'completed' ? 'success' : 'default'}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      }
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="Start Time" secondary={formatDate(task.startTime)} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="End Time" secondary={formatDate(task.endTime)} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="Pages Indexed" secondary={`${task.pagesIndexed} / ${task.maxPages}`} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="Errors" secondary={task.errorCount} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="Crawl Depth" secondary={task.crawlDepth} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="Crawl Strategy" secondary={task.crawlType} />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Documentation Map
              </Typography>
              <Box sx={{ mt: 2 }}>
                <List dense>
                  {renderDocumentTree(task.documentMap)}
                </List>
              </Box>
            </Paper>

            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recently Indexed Pages
              </Typography>
              <List>
                {task.recentPages.map((page: any, index: number) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={page.title}
                        secondary={page.url}
                        primaryTypographyProps={{ fontWeight: 'medium' }}
                      />
                    </ListItem>
                    {index < task.recentPages.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default TaskDetailPage; 