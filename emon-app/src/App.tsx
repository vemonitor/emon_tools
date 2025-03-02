import Layout from '@/layout';
import { Route, Routes } from 'react-router';
import { routes } from './routes/routes';
import { createElement } from 'react';


function App() {

  
  return (
    <Layout>
      <Routes>
        {routes.map((route, i) => (
          route.routes ? (
            <Route
              key={i}
              path={route.path}
            >
              <Route
                  index
                  element={createElement(route.element)}
                />
              {route.routes.map((subroute, j) => (
                <Route
                  key={`${i}_${j}`}
                  path={subroute.path}
                  element={createElement(subroute.element)}
                />
              ))}
            </Route>
          ) : (
            <Route
              key={i}
              path={route.path}
              element={createElement(route.element)}
            />
          )
        ))}
      </Routes>
    </Layout>
  )
}

export default App
