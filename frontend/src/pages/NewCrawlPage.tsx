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
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

const NewCrawlPage: React.FC = () => {
  const [url, setUrl] = useState('');
  const [depth, setDepth] = useState<number>(3);
  const [maxPages, setMaxPages] = useState<number>(100);
  const [crawlType, setCrawlType] = useState('breadth');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log({
      url,
      depth,
      maxPages,
      crawlType,
    });
    // TODO: Implement API call to start a new crawl
    alert('Crawl started! This is a placeholder. In a real app, it would start a crawl job.');
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom align="center" sx={{ mt: 4, mb: 4 }}>
        Start a New Documentation Crawl
      </Typography>

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
                />
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl component="fieldset">
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

            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Maximum Pages to Crawl (10-500)
                  <Tooltip title="Limits the total number of pages that will be processed">
                    <IconButton size="small" sx={{ ml: 1 }}>
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Slider
                  value={maxPages}
                  onChange={(_, newValue) => setMaxPages(newValue as number)}
                  valueLabelDisplay="auto"
                  step={10}
                  marks={[
                    { value: 10, label: '10' },
                    { value: 100, label: '100' },
                    { value: 250, label: '250' },
                    { value: 500, label: '500' },
                  ]}
                  min={10}
                  max={500}
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
                  sx={{ mt: 2, width: '150px' }}
                />
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
                >
                  Start Crawl
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