import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Tooltip,
  LinearProgress,
  Alert,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { ApiService } from '../services/api';
import { CrawlTask } from '../types';

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<CrawlTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await ApiService.getAllTasks();
      setTasks(tasksData);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError('Failed to load tasks. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
  }, []);

  const getStatusChip = (status: string) => {
    let color:
      | 'default'
      | 'primary'
      | 'secondary'
      | 'error'
      | 'info'
      | 'success'
      | 'warning';
    
    switch (status) {
      case 'completed':
        color = 'success';
        break;
      case 'crawling':
      case 'in_progress':
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

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Crawl Tasks</Typography>
          <Button
            component={RouterLink}
            to="/new-crawl"
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
          >
            New Crawl
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
            <Button 
              onClick={fetchTasks} 
              color="inherit" 
              size="small" 
              sx={{ ml: 2 }}
            >
              Retry
            </Button>
          </Alert>
        )}
        
        <TableContainer component={Paper}>
          {loading && <LinearProgress />}
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>URL</TableCell>
                <TableCell>Start Time</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Pages Indexed</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((task) => (
                <TableRow key={task.task_id}>
                  <TableCell>{task.task_id.substring(0, 8)}...</TableCell>
                  <TableCell>
                    <Tooltip title={task.url}>
                      <span>{task.url.length > 30 ? `${task.url.substring(0, 30)}...` : task.url}</span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{formatDate(task.start_time)}</TableCell>
                  <TableCell>{getStatusChip(task.status)}</TableCell>
                  <TableCell>
                    <Tooltip title={task.stats?.max_pages ? `Maximum limit: ${task.stats.max_pages} pages` : ''}>
                      <span>
                        {task.stats?.pages_indexed !== undefined 
                          ? `${task.stats.pages_indexed} ${task.stats.max_pages ? `/ ${task.stats.max_pages}` : ''}`
                          : 'N/A'
                        }
                      </span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Button
                      component={RouterLink}
                      to={`/task/${task.task_id}`}
                      variant="outlined"
                      size="small"
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {!loading && tasks.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No tasks found. Start a new crawl to see results here.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
};

export default TasksPage; 