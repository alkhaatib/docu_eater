import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Slider,
  Grid,
  InputAdornment,
  Tooltip,
  IconButton,
  Stack,
  Alert,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { ApiService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const NewCrawlPage: React.FC = () => {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [depth, setDepth] = useState<number>(3);
  const [maxPages, setMaxPages] = useState<number>(100);
  const [crawlType, setCrawlType] = useState('breadth');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    // Make sure URL has http:// or https:// protocol
    let formattedUrl = url.trim();
    if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
      formattedUrl = 'https://' + formattedUrl;
      setUrl(formattedUrl);
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.startCrawl({
        url: formattedUrl,
        max_depth: depth,
        max_pages: maxPages,
        crawl_type: crawlType
      });
      
      // Navigate to the task detail page
      navigate(`/task/${response.task_id}`);
    } catch (err: any) {
      console.error('Error starting crawl:', err);
      setError(err.message || 'Failed to start crawl. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom align="center" sx={{ mt: 4, mb: 4 }}>
        Start a New Documentation Crawl
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Documentation URL"
                variant="outlined"
                placeholder="https://docs.example.com/"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                disabled={loading}
                helperText="Enter the root URL of the documentation you want to crawl"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Crawl Depth (1-10)
                  <Tooltip title="The number of links to follow from the starting page">
                    <IconButton size="small" sx={{ ml: 1 }}>
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Slider
                  value={depth}
                  onChange={(_, newValue) => setDepth(newValue as number)}
                  valueLabelDisplay="auto"
                  step={1}
                  marks
                  min={1}
                  max={10}
                  disabled={loading}
                />
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl component="fieldset" disabled={loading}>
                <FormLabel component="legend">Crawl Strategy</FormLabel>
                <RadioGroup
                  value={crawlType}
                  onChange={(e) => setCrawlType(e.target.value)}
                >
                  <FormControlLabel
                    value="breadth"
                    control={<Radio />}
                    label="Breadth-first (explore level by level)"
                  />
                  <FormControlLabel
                    value="depth"
                    control={<Radio />}
                    label="Depth-first (follow each path to its end)"
                  />
                </RadioGroup>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box>
                <Typography gutterBottom display="flex" alignItems="center">
                  Max Pages
                  <Tooltip title="Limits the total number of pages that will be processed">
                    <IconButton size="small" sx={{ ml: 0.5, mb: 0.5 }}>
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Slider
                    value={maxPages}
                    onChange={(_, newValue) => setMaxPages(newValue as number)}
                    valueLabelDisplay="auto"
                    step={10}
                    marks={[
                      { value: 10, label: '10' },
                      { value: 500, label: '500' },
                    ]}
                    min={10}
                    max={500}
                    sx={{ width: '150px' }}
                    disabled={loading}
                  />
                  <TextField
                    size="small"
                    type="number"
                    value={maxPages}
                    onChange={(e) => {
                      const value = parseInt(e.target.value);
                      if (value >= 10 && value <= 500) {
                        setMaxPages(value);
                      }
                    }}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">pages</InputAdornment>,
                    }}
                    sx={{ width: '110px' }}
                    disabled={loading}
                  />
                </Stack>
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  size="large"
                  sx={{ minWidth: 200 }}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
                      Starting Crawl...
                    </>
                  ) : (
                    'Start Crawl'
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default NewCrawlPage; 