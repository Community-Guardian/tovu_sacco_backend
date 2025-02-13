from rest_framework import viewsets, status,filters,permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction, LoanTransaction, InvestmentTransaction, SavingTransaction, MinimumSharesDepositTransaction, AuditTransaction,Loan
from .serializers import TransferTransactionSerializer, WithdrawTransactionSerializer, RefundTransactionSerializer, DepositTransactionSerializer, LoanTransactionSerializer, InvestmentTransactionSerializer, SavingTransactionSerializer, MinimumSharesDepositTransactionSerializer, AuditTransactionSerializer
from payments.factory import PaymentServiceFactory
from payments.mpesa_withdrawal_service import MpesaWithdrawalService
from payments.mpesa import MpesaPaymentService
from rest_framework.views import APIView
from accounts.models import Account
from savings.models import Goal
from django.utils import timezone
from .models import InvestmentTransaction, Investment
from django_filters.rest_framework import DjangoFilterBackend
from .filters import InvestmentTransactionFilter, BaseTransactionFilter, SavingTransactionFilter, LoanTransactionFilter, RefundTransactionFilter, DepositTransactionFilter, WithdrawTransactionFilter, TransferTransactionFilter, MinimumSharesDepositTransactionFilter
class TransferTransactionViewSet(viewsets.ModelViewSet):
    queryset = TransferTransaction.objects.all()
    serializer_class = TransferTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransferTransactionFilter
    search_fields = ['sender_account', 'receiver_account', 'sender_goal', 'receiver_goal']
    ordering_fields = ['sender_account', 'receiver_account', 'sender_goal', 'receiver_goal']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def create_transfer(self, request):
        data = request.data.copy()
        if 'user' not in data:
            data['user'] = request.user.id

        sender_account_id = data.get('sender_account')
        receiver_account_id = data.get('receiver_account')
        sender_goal_id = data.get('sender_goal')
        receiver_goal_id = data.get('receiver_goal')
        amount = data.get('amount')

        # Validate sender and receiver
        if not sender_account_id and not sender_goal_id:
            return Response({'error': 'Sender account or goal must be provided.'}, status=400)
        if not receiver_account_id and not receiver_goal_id:
            return Response({'error': 'Receiver account or goal must be provided.'}, status=400)
        if (sender_account_id and sender_account_id == receiver_account_id) :
            return Response({'error': 'Cannot transfer to the same account '}, status=400)
        try:
            if sender_account_id:
                sender_account = Account.objects.get(pk=sender_account_id)
                if sender_account.user != request.user:
                    return Response({'error': 'Sender account does not belong to the user.'}, status=400)
            else:
                sender_account = None

            if receiver_account_id:
                receiver_account = Account.objects.get(pk=receiver_account_id)
                # if receiver_account.user != request.user:
                #     return Response({'error': 'Receiver account does not belong to the user.'}, status=400)
            else:
                receiver_account = None

            if sender_goal_id:
                sender_goal = Goal.objects.get(pk=sender_goal_id)
                if sender_goal.account.user != request.user:
                    return Response({'error': 'Sender goal does not belong to the user.'}, status=400)
            else:
                sender_goal = None

            if receiver_goal_id:
                receiver_goal = Goal.objects.get(pk=receiver_goal_id)
                if receiver_goal.account.user != request.user:
                    return Response({'error': 'Receiver goal does not belong to the user.'}, status=400)
            else:
                receiver_goal = None

            # Ensure the sender has enough balance
            if sender_account and sender_account.account_balance < amount:
                return Response({'error': 'Insufficient funds in sender account.'}, status=400)
            if sender_goal and sender_goal.current_amount < amount:
                return Response({'error': 'Insufficient funds in sender goal.'}, status=400)

            # Perform the transfer
            if sender_account:
                sender_account.account_balance -= amount
                sender_account.save()
            if sender_goal:
                sender_goal.current_amount -= amount
                sender_goal.save()

            if receiver_account:
                receiver_account.account_balance += amount
                receiver_account.save()
            if receiver_goal:
                receiver_goal.current_amount += amount
                receiver_goal.save()

            # Create the transfer transaction
            data['payment_method'] = 'in-house'
            data['status'] = 'completed'
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist.'}, status=400)
        except Goal.DoesNotExist:
            return Response({'error': 'Goal does not exist.'}, status=400)

class WithdrawTransactionViewSet(viewsets.ModelViewSet):
    queryset = WithdrawTransaction.objects.all()
    serializer_class = WithdrawTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WithdrawTransactionFilter
    search_fields = ['account']
    ordering_fields = ['account', 'date']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def initiate_withdrawal(self, request):
        data = request.data
        payment_method = data.get('payment_method')
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        description = data.get('description', 'Withdrawal via M-Pesa')
        account_id = data.get('account_id')

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
            if(account.user != request.user):
                return Response({'error': 'Account does not belong to the user'}, status=400)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist'}, status=400)

        try:
            if payment_method == "mpesa":
                transaction = MpesaWithdrawalService.initiate_withdrawal(phone_number, amount, description, request.user, account)
                return Response({'transaction_id': transaction.transaction_id}, status=201)
            else:
                return Response({'error': 'Unsupported payment method'}, status=400)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'An error occurred while initiating the withdrawal.'}, status=500)

class RefundTransactionViewSet(viewsets.ModelViewSet):
    queryset = RefundTransaction.objects.all()
    serializer_class = RefundTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RefundTransactionFilter
    search_fields = ['account']
    ordering_fields = ['account', 'date']
    ordering = ['-date']

class DepositTransactionViewSet(viewsets.ModelViewSet):
    queryset = DepositTransaction.objects.all()
    serializer_class = DepositTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DepositTransactionFilter
    search_fields = ['account']
    ordering_fields = ['account', 'date']
    ordering = ['-date']
    

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        data = request.data
        payment_method = data.get('payment_method')
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        description = data.get('description', 'Payment via M-Pesa')
        account_id = data.get('account_id')

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist'}, status=400)

        try:
            payment_service = PaymentServiceFactory.get_payment_service(payment_method)
            transaction = payment_service.initiate_payment(phone_number, amount, description, request.user, account)
            print(transaction)
            transaction.save()
            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
class LoanTransactionViewSet(viewsets.ModelViewSet):
    queryset = LoanTransaction.objects.all()
    serializer_class = LoanTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LoanTransactionFilter
    search_fields = ['loan']
    ordering_fields = ['loan', 'date']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def pay_loan(self, request):
        data = request.data
        payment_method = data.get('payment_method')
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        description = data.get('description', 'Loan Payment')
        loan_id = data.get('loan_id')
        account_id = data.get('account_id')

        # Validate loan
        try:
            loan = Loan.objects.get(pk=loan_id)
            if loan.status != "approved":
                return Response({'error': 'Only disbursed loans can be paid for.'}, status=400)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan does not exist.'}, status=400)

        # Validate account if provided
        if account_id:
            try:
                account = Account.objects.get(pk=account_id)
                if account.user != request.user:
                    return Response({'error': 'Account does not belong to the user.'}, status=400)
                if account.account_balance < amount:
                    return Response({'error': 'Insufficient funds in account.'}, status=400)
            except Account.DoesNotExist:
                return Response({'error': 'Account does not exist.'}, status=400)
        else:
            account = None

        try:
            if payment_method == "mpesa":
                payment_service = PaymentServiceFactory.get_payment_service(payment_method)
                transaction = payment_service.initiate_payment(phone_number, amount, description, request.user,account)
                transaction.loan = loan
                transaction.save()
            elif account:
                # Deduct amount from account balance
                account.account_balance -= amount
                account.save()

                # Create loan transaction
                transaction = LoanTransaction.objects.create(
                    user=request.user,
                    loan=loan,
                    amount=amount,
                    description=description,
                    status="completed",
                    payment_method="in-house",
                    transaction_type="loan"
                )
            else:
                return Response({'error': 'Unsupported payment method or missing account.'}, status=400)

            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'An error occurred while initiating the payment.'}, status=500)

class InvestmentTransactionViewSet(viewsets.ModelViewSet):
    queryset = InvestmentTransaction.objects.all()
    serializer_class = InvestmentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InvestmentTransactionFilter
    search_fields = ['investment']
    ordering_fields = ['investment', 'date']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        data = request.data
        investment_id = data.get('investment_id')
        amount = data.get('amount')
        description = data.get('description', 'Investment Deposit')
        account_id = data.get('account_id')

        # Validate investment
        try:
            investment = Investment.objects.get(pk=investment_id)
            if not investment.is_active:
                return Response({'error': 'Cannot deposit into an inactive investment.'}, status=400)
        except Investment.DoesNotExist:
            return Response({'error': 'Investment does not exist.'}, status=400)

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
            if account.user != request.user:
                return Response({'error': 'Account does not belong to the user.'}, status=400)
            if account.account_balance < amount:
                return Response({'error': 'Insufficient funds in account.'}, status=400)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist.'}, status=400)

        try:
            # Deduct amount from account balance
            account.account_balance -= amount
            account.save()

            # Create investment transaction
            transaction = InvestmentTransaction.objects.create(
                user=request.user,
                investment=investment,
                amount=amount,
                description=description,
                status="completed",
                payment_method="in-house",
                transaction_type="investment"
            )

            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except Exception as e:
            return Response({'error': 'An error occurred while processing the deposit.'}, status=500)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        data = request.data
        investment_id = data.get('investment_id')
        amount = data.get('amount')
        description = data.get('description', 'Investment Withdrawal')
        account_id = data.get('account_id')

        # Validate investment
        try:
            investment = Investment.objects.get(pk=investment_id)
            if not investment.is_active:
                return Response({'error': 'Cannot withdraw from an inactive investment.'}, status=400)
            if investment.maturity_date > timezone.now():
                return Response({'error': 'Cannot withdraw before the maturity date.'}, status=400)
        except Investment.DoesNotExist:
            return Response({'error': 'Investment does not exist.'}, status=400)

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
            if account.user != request.user:
                return Response({'error': 'Account does not belong to the user.'}, status=400)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist.'}, status=400)

        try:
            # Create investment transaction
            transaction = InvestmentTransaction.objects.create(
                user=request.user,
                investment=investment,
                amount=amount,
                description=description,
                status="completed",
                payment_method="in-house",
                transaction_type="withdraw"
            )

            # Add amount to account balance
            account.account_balance += amount
            account.save()

            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except Exception as e:
            return Response({'error': 'An error occurred while processing the withdrawal.'}, status=500)
class SavingTransactionViewSet(viewsets.ModelViewSet):
    queryset = SavingTransaction.objects.all()
    serializer_class = SavingTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SavingTransactionFilter
    search_fields = ['goal']
    ordering_fields = ['goal', 'date']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        data = request.data
        goal_id = data.get('goal_id')
        amount = data.get('amount')
        description = data.get('description', 'Saving Deposit')
        account_id = data.get('account_id')

        # Validate goal
        try:
            goal = Goal.objects.get(pk=goal_id, account__user=request.user)
        except Goal.DoesNotExist:
            return Response({'error': 'Goal does not exist or not authorized.'}, status=400)

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
            if account.user != request.user:
                return Response({'error': 'Account does not belong to the user.'}, status=400)
            if account.account_balance < amount:
                return Response({'error': 'Insufficient funds in account.'}, status=400)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist.'}, status=400)

        try:
            # Deduct amount from account balance
            account.account_balance -= amount
            account.save()

            # Update goal amount
            goal.current_amount += amount
            goal.save()

            # Create saving transaction
            transaction = SavingTransaction.objects.create(
                user=request.user,
                goal=goal,
                amount=amount,
                description=description,
                status="completed",
                payment_method="in-house",
                transaction_type="saving"
            )

            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except Exception as e:
            return Response({'error': 'An error occurred while processing the deposit.'}, status=500)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        data = request.data
        goal_id = data.get('goal_id')
        amount = data.get('amount')
        description = data.get('description', 'Saving Withdrawal')
        account_id = data.get('account_id')

        # Validate goal
        try:
            goal = Goal.objects.get(pk=goal_id, account__user=request.user)
            if goal.current_amount < amount:
                return Response({'error': 'Insufficient funds in goal.'}, status=400)
        except Goal.DoesNotExist:
            return Response({'error': 'Goal does not exist or not authorized.'}, status=400)

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
            if account.user != request.user:
                return Response({'error': 'Account does not belong to the user.'}, status=400)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist.'}, status=400)

        try:
            # Deduct amount from goal
            goal.current_amount -= amount
            goal.save()

            # Add amount to account balance
            account.account_balance += amount
            account.save()

            # Create saving transaction
            transaction = SavingTransaction.objects.create(
                user=request.user,
                goal=goal,
                amount=amount,
                description=description,
                status="completed",
                payment_method="in-house",
                transaction_type="withdraw"
            )

            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except Exception as e:
            return Response({'error': 'An error occurred while processing the withdrawal.'}, status=500)
class MinimumSharesDepositTransactionViewSet(viewsets.ModelViewSet):
    queryset = MinimumSharesDepositTransaction.objects.all()
    serializer_class = MinimumSharesDepositTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MinimumSharesDepositTransactionFilter
    search_fields = ['description']
    ordering_fields = ['description', 'date']
    ordering = ['-date']

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        data = request.data
        payment_method = data.get('payment_method')
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        description = data.get('description', 'Minimum Shares Deposit via M-Pesa')
        account_id = data.get('account_id')

        # Validate account
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return Response({'error': 'Account does not exist'}, status=400)
        try:
            payment_service = PaymentServiceFactory.get_payment_service(payment_method)
            transaction = payment_service.initiate_payment(phone_number, amount, description, request.user, account)
            return Response({'transaction_id': transaction.transaction_id}, status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'An error occurred while initiating the payment.'}, status=500)
class AuditTransactionViewSet(viewsets.ModelViewSet):
    queryset = AuditTransaction.objects.all()
    serializer_class = AuditTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['transaction_id'] 
    ordering_fields = ['transaction_id', 'updated_at']
    ordering = ['-updated_at']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Ensure AuditTransaction deletes correctly
        AuditTransaction.objects.filter(transaction_type=instance.__class__, transaction_id=instance.id).delete()
        instance.delete()
        return Response({"message": "DepositTransaction deleted successfully"}, status=204)
class MpesaCallbackView(APIView):
    """
    API endpoint for handling M-Pesa callbacks.
    """
    permission_classes = []
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            if 'stkCallback' in data.get('Body', {}):
                MpesaPaymentService.handle_callback(data)
            elif 'Result' in data:
                MpesaWithdrawalService.handle_withdrawal_callback(data)
            else:
                return Response({'error': 'Invalid callback data'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)