import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { validateStringId } from "@/lib/utils";
import { Link, useNavigate, useParams } from "react-router";

function DeleteDataPath() {
  const { fetchWithAuth } = useAuth();
  const { path_id } = useParams();
  const navigate = useNavigate();
  const itemId = validateStringId(path_id)
  const DeleteDataPathAction = async () => {
    if(!itemId || itemId <= 0){
      return new Error(
        "Unable to delete Item, id is invalid"
      )
    }
    try {
      const response = await fetchWithAuth(
        `/api/v1/category/data_path/${itemId}/`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      ).then((response) => response.json())
      if (!response.success) {
        return {
          success: false,
          msg: response.msg,
          errors: response.errors,
          from_error: response.from_error,
        }
      }
    } catch (error: unknown) {
      console.log('Error fetching data:', error);
      return {
        success: false,
        msg: 'Unable to save data, please control all fields',
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
    navigate("/data-path")
    return;
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Delete Item: Are you absolutely sure?</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="">
          This action cannot be undone. This will permanently delete data path item
          and remove your data from our servers.
        </div>
        <Button
          variant="destructive"
          onClick={DeleteDataPathAction}
        >
          Delete
        </Button>
        <Button variant="ghost">
          <Link to="/data-path">Back</Link>
        </Button>
      </CardContent>
    </Card>
  )
}

export default DeleteDataPath