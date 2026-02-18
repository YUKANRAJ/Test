public class OnlDri {
    
    public static void main(String[] args) {
        Online Credit=new Creditcard();
        Online Upi=new Upi();
        Credit.setAmount(200);
        Upi.setAmount(200);
        Credit.pay();
        Upi.pay();

    }
}
