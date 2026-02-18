public class Creditcard extends Online{

    public void pay()
    {
        double tax=0;
        tax=getAmount()*(0.18);
        System.out.println("---------------Credit Card--------------------");
        System.out.println("Your amount is "+getAmount()+" only");
        System.out.println("You have paid through credit card so you will have 18 percent service tax ");
        System.out.println("Your final Amount is "+(getAmount()+tax)+" only ");
        System.out.println("Thank you for Shopping");


    }
    
}
