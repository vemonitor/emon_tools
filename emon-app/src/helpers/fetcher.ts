type getWithFetchProps = {
  url: string
}

type postWithFetchProps = {
  url: string,
  method: string,
  data: object
}

export const getWithFetch = async ({
  url
}: getWithFetchProps) => {
  const response = await fetch(
    url,
    {
      method: 'GET',
      /*headers: {
        'Accept': 'application/json',
        'content-type': 'application/json',
        'X-API-Key': api_key
      }*/
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error: Status ${response.status}`);
  }

  return response.json();
};

export const postWithFetch = async ({
  url,
  method,
  data
}: postWithFetchProps) => {
    const response = await fetch(
      url,
      {
        method: method,
        /*headers: {
          'content-type': 'application/json',
          'X-API-Key': api_key
        },*/
        body: JSON.stringify(data),
      }
    );
  
    if (!response.ok) {
      throw new Error(`HTTP error: Status ${response.status}`);
    }
  
    return response.json();
  };