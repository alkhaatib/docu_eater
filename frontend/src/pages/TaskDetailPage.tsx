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
  Alert,
  Button,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import { Link as RouterLink } from 'react-router-dom';
import { ApiService } from '../services/api';
import { CrawlTask, DocMap } from '../types';

const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<CrawlTask | null>(null);
  const [docMap, setDocMap] = useState<DocMap | null>(null);
  const [loading, setLoading] = useState(true);
  const [docMapLoading, setDocMapLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [docMapError, setDocMapError] = useState<string | null>(null);

  // Polling interval for task status (in ms)
  const POLL_INTERVAL = 3000;

  useEffect(() => {
    if (!taskId) {
      setError('Task ID is missing.');
      setLoading(false);
      return;
    }

    let intervalId: NodeJS.Timeout;

    const fetchTaskStatus = async () => {
      try {
        const taskData = await ApiService.getCrawlStatus(taskId);
        setTask(taskData);

        // If task is completed, try to fetch the documentation map
        if (taskData.status === 'completed' && !docMap && !docMapLoading) {
          fetchDocMap();
        }

        // If task is in a final state (completed or failed), stop polling
        if (taskData.status === 'completed' || taskData.status === 'failed') {
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error('Error fetching task status:', err);
        setError('Failed to load task. Please try again later.');
        clearInterval(intervalId);
      } finally {
        setLoading(false);
      }
    };

    // Fetch initially
    fetchTaskStatus();

    // Set up polling
    intervalId = setInterval(fetchTaskStatus, POLL_INTERVAL);

    // Clean up on unmount
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [taskId, docMap, docMapLoading]);

  const fetchDocMap = async () => {
    if (!taskId) return;

    try {
      setDocMapLoading(true);
      const docMapData = await ApiService.getDocMap(taskId);
      setDocMap(docMapData);
    } catch (err) {
      console.error('Error fetching doc map:', err);
      setDocMapError('Failed to load documentation map.');
    } finally {
      setDocMapLoading(false);
    }
  };

  const renderDocumentTree = (node: DocMap, level = 0) => {
    const isFolder = node.children && node.children.length > 0;
    
    return (
      <React.Fragment key={node.id}>
        <ListItem sx={{ pl: level * 2 }}>
          <ListItemIcon>
            {isFolder ? <FolderIcon color="primary" /> : <DescriptionIcon color="info" />}
          </ListItemIcon>
          <ListItemText 
            primary={node.name} 
            secondary={node.url}
            primaryTypographyProps={{ fontWeight: isFolder ? 'bold' : 'normal' }}
          />
        </ListItem>
        {isFolder && node.children.map((child) => renderDocumentTree(child, level + 1))}
      </React.Fragment>
    );
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getStatusChip = (status: string) => {
    let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
    
    switch (status) {
      case 'completed':
        color = 'success';
        break;
      case 'crawling':
      case 'processing':
        color = 'info';
        break;
      case 'failed':
        color = 'error';
        break;
      case 'queued':
        color = 'warning';
        break;
      default:
        color = 'default';
    }
    
    return (
      <Chip
        label={status.replace('_', ' ')}
        color={color}
        size="small"
      />
    );
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

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Alert severity="error">{error}</Alert>
          <Box sx={{ mt: 2 }}>
            <Button
              component={RouterLink}
              to="/tasks"
              startIcon={<ArrowBackIcon />}
            >
              Back to Tasks
            </Button>
          </Box>
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
          <Box sx={{ mt: 2 }}>
            <Button
              component={RouterLink}
              to="/tasks"
              startIcon={<ArrowBackIcon />}
            >
              Back to Tasks
            </Button>
          </Box>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Button
            component={RouterLink}
            to="/tasks"
            startIcon={<ArrowBackIcon />}
            sx={{ mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h4">
            Task Detail: {taskId}
          </Typography>
        </Box>

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
                      secondary={getStatusChip(task.status)}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="Start Time" secondary={formatDate(task.start_time)} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText primary="End Time" secondary={formatDate(task.end_time)} />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText 
                      primary="Pages Indexed" 
                      secondary={task.stats 
                        ? `${task.stats.pages_indexed || 0} / ${task.stats.max_pages || 'unlimited'}`
                        : 'N/A'
                      } 
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText 
                      primary="Errors" 
                      secondary={task.stats?.errors !== undefined ? task.stats.errors : 'N/A'} 
                    />
                  </ListItem>
                  {task.error && (
                    <>
                      <Divider />
                      <ListItem>
                        <ListItemText 
                          primary="Error Message" 
                          secondary={task.error}
                          secondaryTypographyProps={{ color: 'error' }}
                        />
                      </ListItem>
                    </>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Documentation Map
              </Typography>
              
              {docMapLoading && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Loading documentation map...
                  </Typography>
                </Box>
              )}
              
              {docMapError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {docMapError}
                </Alert>
              )}
              
              {docMap && (
                <Box sx={{ mt: 2 }}>
                  <List dense>
                    {renderDocumentTree(docMap)}
                  </List>
                </Box>
              )}
              
              {!docMap && !docMapLoading && !docMapError && task.status !== 'completed' && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Documentation map will be available once the crawl is completed.
                </Alert>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default TaskDetailPage; 