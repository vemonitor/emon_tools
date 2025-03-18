import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { Link, useNavigate, useParams } from "react-router";
import { z } from 'zod';


const idSchemeIn = z.string()
  .min(1)
  .max(9)
  .regex(/^[0-9]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

const idSchemeOut = z.number()
  .positive();

function DeleteCategory() {
  const { fetchWithAuth } = useAuth();
  const { category_id } = useParams();
  const navigate = useNavigate();
  idSchemeIn.parse(category_id);
  const itemId = category_id ? parseInt(category_id) : 0
  idSchemeOut.parse(itemId);
  const DeleteCategoryAction = async () => {
    if(!itemId || itemId <= 0){
      return new Error(
        "Unable to delete Item, id is invalid"
      )
    }
    try {
      const response = await fetchWithAuth(
        `/api/v1/category/delete/${itemId}/`,
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
    navigate("/category")
    return;
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Delete Item: Are you absolutely sure?</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="">
          This action cannot be undone. This will permanently delete your account
          and remove your data from our servers.
        </div>
        <Button
          variant="destructive"
          onClick={DeleteCategoryAction}
        >
          Delete
        </Button>
        <Button variant="ghost">
          <Link to="/category">Back</Link>
        </Button>
      </CardContent>
    </Card>
  )
}

export default DeleteCategory