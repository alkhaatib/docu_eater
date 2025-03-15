import React from 'react';
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
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

// Mock data - in a real app, this would come from an API
const mockTasks = [
  {
    id: '1',
    url: 'https://docs.python.org',
    startTime: '2023-03-10T08:30:00',
    status: 'completed',
    pagesIndexed: 243,
    maxPages: 300,
  },
  {
    id: '2',
    url: 'https://reactjs.org/docs',
    startTime: '2023-03-12T14:15:00',
    status: 'in_progress',
    pagesIndexed: 56,
    maxPages: 200,
  },
  {
    id: '3',
    url: 'https://docs.docker.com',
    startTime: '2023-03-14T10:45:00',
    status: 'failed',
    pagesIndexed: 12,
    maxPages: 150,
  },
];

const TasksPage: React.FC = () => {
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
      case 'in_progress':
        color = 'info';
        break;
      case 'failed':
        color = 'error';
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Crawl Tasks
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Button
            component={RouterLink}
            to="/new-crawl"
            variant="contained"
            color="primary"
          >
            New Crawl
          </Button>
        </Box>
        
        <TableContainer component={Paper}>
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
              {mockTasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell>{task.id}</TableCell>
                  <TableCell>{task.url}</TableCell>
                  <TableCell>{formatDate(task.startTime)}</TableCell>
                  <TableCell>{getStatusChip(task.status)}</TableCell>
                  <TableCell>
                    <Tooltip title={`Maximum limit: ${task.maxPages} pages`}>
                      <span>{task.pagesIndexed} / {task.maxPages}</span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Button
                      component={RouterLink}
                      to={`/task/${task.id}`}
                      variant="outlined"
                      size="small"
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {mockTasks.length === 0 && (
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