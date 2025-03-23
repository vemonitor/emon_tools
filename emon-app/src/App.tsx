import Layout from '@/layout';
import { Route, Routes } from 'react-router';
import { publicRoutes, privateRoutes, RouteListType } from './routes/routes';
import { createElement } from 'react';
import { useAuth } from './hooks/use-auth';
import Error404 from './routes/404';

function App() {
  const { isAuthenticated } = useAuth();
  const setRoutes = (routes: RouteListType[]) => {
    return routes.map((route, i) => (
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
              element={createElement(subroute.element as React.ComponentType<unknown>)}
            />
          ))}
        </Route>
      ) : (
        <Route
          key={i}
          path={route.path}
          element={createElement(route.element as React.ComponentType<unknown>)}
        />
      )
    ))
  }

  return (
    <Layout>
          <Routes>
            {[
              setRoutes(publicRoutes),
              isAuthenticated ? setRoutes(privateRoutes) : null,
              <Route key={'error-404'} path="*" element={<Error404 />} />
            ]}
          </Routes>
        </Layout>
  )
}

export default App
