import { Button } from '@/components/ui/button';
import { Link } from 'react-router';

function home() {
  return (
    <div className="flex flex-col justify-between min-h-[91vh] bg-background">
      {/* Main content */}
      <main>
        <section className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <div className="text-center">
            <h2 className="text-4xl font-extrabold text-foreground sm:text-5xl">
              Seamless EmonCMS Integration
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Emon Tools provides a streamlined API interface for interacting with EmonCMS, along with robust tools to analyze and visualize PhpFina files.
            </p>
            <div className="mt-8 flex justify-center">
              <a href="https://github.com/vemonitor/emon_tools/wiki" target="_blank" rel="noopener noreferrer">
                <Button variant="default">View Python Package Documentation</Button>
              </a>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div
              className="p-6 rounded-lg shadow"
              style={{ backgroundColor: 'hsl(var(--card))' }}
            >
              <h3 className="text-2xl font-bold text-foreground">
                Emon Fina Reader
              </h3>
              <p className="mt-2 text-muted-foreground">
                Efficiently read and analyze time-series data from Archived PhpFina file formats.
                Compute daily stats, filter data, and manipulate timestamps.
              </p>
              <div className="mt-4">
                <Link to="/dataViewer/fina">
                  <Button variant="outline">Learn More</Button>
                </Link>
              </div>
            </div>
            <div
              className="p-6 rounded-lg shadow"
              style={{ backgroundColor: 'hsl(var(--card))' }}
            >
              <h3 className="text-2xl font-bold text-foreground">
                Emoncms
              </h3>
              <p className="mt-2 text-muted-foreground">
                Easily interact with all your EmonCMS instances.<br />
                Manage data structures with ease.
              </p>
              <div className="mt-4">
                <Link to="/dataViewer/hosted">
                  <Button variant="outline">Learn More</Button>
                </Link>
              </div>
            </div>
          </div>

          
        </section>
      </main>

      {/* Footer */}
      <footer
        className="py-4"
        style={{ backgroundColor: 'hsl(var(--secondary))' }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Emon Tools. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default home